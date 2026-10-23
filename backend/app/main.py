"""
Main FastAPI application module.

This is the entry point for the CTrack backend API.
It configures:
- FastAPI application with metadata
- CORS middleware for frontend communication
- Rate limiting for API protection
- Global exception handlers
- API routers for all endpoints
- Database initialization
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.routers import osmoseur_router, remplisseuse_router, iot_osmoseur_router
from app.routers import auth, admin, technicians
from app.routers import incident  # Import Incident Router
from app.routers import notification as notification_router  # Import Notification Router
from app.routers import ml_insights  # Import ML Insights Router
from app.routers import ml_advanced  # Import Advanced ML Router
from app.routers import ai_chat  # Import AI Chat Router
from analytics.router import router as analytics_router
from app.services.ws_manager import ws_manager
from app.services.scheduler import deadline_scheduler
from app.jobs.inference_scheduler import inference_worker

import asyncio
from fastapi import WebSocket, WebSocketDisconnect


# ============================================================================
# RATE LIMITER CONFIGURATION
# ============================================================================

limiter = Limiter(key_func=get_remote_address)
"""
Rate limiter instance.

Limits API requests per IP address to prevent abuse.
Default: 60 requests per minute (configured in settings)
"""


# ============================================================================
# APPLICATION LIFECYCLE MANAGEMENT
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    
    Handles startup and shutdown events:
    - Startup: Create database tables (development only)
    - Shutdown: Cleanup resources
    
    In production, use Alembic migrations instead of creating tables on startup.
    """
    # Startup: Create database tables
    print("Starting CTrack API...")

    # Refuse to run in production with a placeholder JWT secret (tokens could be forged)
    if not settings.DEBUG and (
        len(settings.SECRET_KEY) < 32 or "change-this-in-production" in settings.SECRET_KEY
    ):
        raise RuntimeError(
            "SECRET_KEY is missing or still a placeholder. "
            "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
        )

    # Store the main event loop for background WebSocket pushes
    # so sync endpoints can dispatch async tasks.
    ws_manager.loop = asyncio.get_running_loop()

    print(f"Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")
    
    # Create tables (only for development - use Alembic in production)
    if settings.DEBUG:
        print("DEBUG MODE: Creating database tables...")
        # Ensure the 'iot' schema exists before creating tables
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS iot"))
            conn.commit()
        Base.metadata.create_all(bind=engine)
        print("Database tables created")

    # Start deadline scheduler (interval set by DEADLINE_CHECK_INTERVAL_SECONDS)
    scheduler_task = asyncio.create_task(
        deadline_scheduler(interval_seconds=settings.DEADLINE_CHECK_INTERVAL_SECONDS)
    )
    print(f"Deadline notification scheduler started (every {settings.DEADLINE_CHECK_INTERVAL_SECONDS}s)")

    # Start ML inference worker (interval set by INFERENCE_INTERVAL_SECONDS)
    inference_task = asyncio.create_task(
        inference_worker(interval_seconds=settings.INFERENCE_INTERVAL_SECONDS)
    )
    print(f"ML Inference background worker started (every {settings.INFERENCE_INTERVAL_SECONDS}s)")
    
    yield
    
    # Shutdown: Cleanup
    scheduler_task.cancel()
    inference_task.cancel()
    print("Shutting down CTrack API...")


# ============================================================================
# FASTAPI APPLICATION INSTANCE
# ============================================================================

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    # CTrack Industrial Monitoring API
    
    Professional REST API for monitoring and managing industrial machine data.
    
    ## Features
    
    - **Osmoseur Machine**: Monitor reverse osmosis water treatment parameters
    - **Remplisseuse Machine**: Track filling machine performance and quality
    - **Real-time Data**: Create, read, update, and delete machine records
    - **Analytics**: Statistical summaries and trends
    - **Pagination**: Efficient data retrieval with pagination support
    - **Sorting**: Flexible sorting options for all endpoints
    
    ## Authentication
    
    This API uses JWT (JSON Web Token) authentication for secure access.
    Include the token in the Authorization header:
    ```
    Authorization: Bearer <your-token>
    ```
    
    ## Rate Limiting
    
    API requests are limited to {rate_limit} requests per minute per IP address.
    """.format(rate_limit=settings.RATE_LIMIT_PER_MINUTE),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    debug=settings.DEBUG
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ============================================================================
# CORS MIDDLEWARE CONFIGURATION
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # List of allowed origins (e.g., Next.js frontend)
    allow_credentials=True,                     # Allow cookies and authentication headers
    allow_methods=["*"],                        # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],                        # Allow all headers
    expose_headers=["*"]                        # Expose all headers to the frontend
)
"""
CORS (Cross-Origin Resource Sharing) middleware.

Allows the Next.js frontend (running on localhost:3000) to communicate with the API.

Configuration:
- allow_origins: Permitted frontend URLs (from settings.CORS_ORIGINS)
- allow_credentials: Enables sending cookies and auth headers
- allow_methods: All HTTP methods allowed
- allow_headers: All request headers allowed
"""


# ============================================================================
# GLOBAL EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.
    
    Catches any unhandled exceptions and returns a standardized error response.
    In production, this prevents exposing internal error details to clients.
    
    Args:
        request: The incoming request
        exc: The exception that was raised
        
    Returns:
        JSONResponse with error details
    """
    # Log the error (in production, use proper logging)
    print(f"Unhandled error: {str(exc)}")
    
    # Return user-friendly error response
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred",
            "error": str(exc) if settings.DEBUG else "Internal server error"
        }
    )


# ============================================================================
# API ROUTERS REGISTRATION
# ============================================================================

# Include Osmoseur router
app.include_router(
    osmoseur_router,
    prefix=settings.API_V1_PREFIX,
    tags=["Osmoseur"]
)

# Include Remplisseuse router
app.include_router(
    remplisseuse_router,
    prefix=settings.API_V1_PREFIX,
    tags=["Remplisseuse"]
)

# Include Auth router
app.include_router(auth.router)

# Include Admin Data Warehouse router
app.include_router(admin.router)

# Include Analytics router
app.include_router(analytics_router)

# Include Technicians Management router
app.include_router(technicians.router)

# Include Incident Management router
app.include_router(
    incident.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Incidents"]
)

# Include Notification router
app.include_router(
    notification_router.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Notifications"]
)



# Include Machine Learning router
app.include_router(ml_insights.router)

# Include Advanced Machine Learning router
app.include_router(ml_advanced.router)

# Include IoT Osmoseur router
app.include_router(
    iot_osmoseur_router,
    prefix=settings.API_V1_PREFIX,
    tags=["IoT Osmoseur"],
)

# Include AI Chat router
app.include_router(
    ai_chat.router,
    prefix=settings.API_V1_PREFIX,
    tags=["AI Chatbot"]
)


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@app.websocket("/ws/notifications/{user_id}")
async def websocket_notifications(websocket: WebSocket, user_id: int):
    """
    WebSocket endpoint for real-time notification delivery.
    Client connects with user_id to receive push notifications.
    """
    await ws_manager.connect(user_id, websocket)
    try:
        while True:
            # Keep connection alive; listen for pings
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(user_id)


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get(
    "/",
    tags=["Root"],
    summary="API Root",
    description="Welcome endpoint with API information"
)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def root(request: Request):
    """
    Root endpoint providing API information.
    
    Returns basic information about the API and available endpoints.
    
    **Rate Limited:** {rate_limit} requests per minute
    
    **Returns:**
    ```json
    {
        "message": "Welcome to CTrack API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }
    ```
    """.format(rate_limit=settings.RATE_LIMIT_PER_MINUTE)
    
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "osmoseur": f"{settings.API_V1_PREFIX}/osmoseur",
            "remplisseuse": f"{settings.API_V1_PREFIX}/remplisseuse"
        }
    }


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.get(
    "/health",
    tags=["Health"],
    summary="Health Check",
    description="Check if the API is running and database is accessible"
)
async def health_check():
    """
    Health check endpoint.
    
    Used by monitoring systems and load balancers to verify API availability.
    
    **Returns:**
    ```json
    {
        "status": "healthy",
        "database": "connected"
    }
    ```
    """
    # TODO: Add actual database connectivity check
    return {
        "status": "healthy",
        "database": "connected"
    }


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    """
    Run the application using Uvicorn ASGI server.
    
    This is for development only. In production, use:
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
    """
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,  # Auto-reload on code changes in debug mode
        log_level="info"
    )

# Force reload for AI package
