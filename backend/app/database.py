"""
Database connection and session management module.

This module sets up SQLAlchemy for PostgreSQL database operations:
- Creates database engine with connection pooling
- Provides session factory for database transactions
- Defines Base class for all ORM models
- Provides dependency injection for FastAPI routes
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Generator

from app.config import settings


# ============================================================================
# DATABASE ENGINE CONFIGURATION
# ============================================================================

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=5,          # Number of connections to maintain
    max_overflow=10,      # Maximum number of connections to create beyond pool_size
    echo=settings.DEBUG,   # Log all SQL statements when DEBUG=True
    connect_args={"client_encoding": "utf8"}  # Force UTF-8 encoding for client communication
)
"""
SQLAlchemy database engine.

The engine manages database connections and connection pooling.
- pool_pre_ping: Ensures connections are alive before use
- pool_size: Number of persistent connections
- max_overflow: Additional connections when pool is exhausted
- echo: Logs SQL queries in debug mode
"""


# ============================================================================
# SESSION FACTORY
# ============================================================================

SessionLocal = sessionmaker(
    autocommit=False,  # Transactions must be explicitly committed
    autoflush=False,   # Don't automatically flush changes
    bind=engine        # Bind to our database engine
)
"""
Session factory for creating database sessions.

Each session represents a database transaction.
Sessions should be closed after use to return connections to the pool.
"""


# ============================================================================
# BASE CLASS FOR ORM MODELS
# ============================================================================

Base = declarative_base()
"""
Base class for all SQLAlchemy ORM models.

All database models should inherit from this class.

Example:
    class MyModel(Base):
        __tablename__ = "my_table"
        id = Column(Integer, primary_key=True)
"""


# ============================================================================
# DATABASE DEPENDENCY FOR FASTAPI
# ============================================================================

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.
    
    This function creates a new database session for each request
    and automatically closes it when the request is complete.
    
    Usage in FastAPI routes:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            items = db.query(Item).all()
            return items
    
    Yields:
        Session: SQLAlchemy database session
        
    Note:
        The session is automatically closed in the finally block,
        ensuring connections are returned to the pool even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# DATABASE INITIALIZATION FUNCTIONS
# ============================================================================

def create_tables():
    """
    Create all database tables defined in ORM models.
    
    This function should only be used in development.
    In production, use Alembic migrations instead.
    
    Usage:
        from app.database import create_tables
        create_tables()
    """
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    Drop all database tables.
    
    WARNING: This will delete all data!
    Only use this in development/testing.
    
    Usage:
        from app.database import drop_tables
        drop_tables()
    """
    Base.metadata.drop_all(bind=engine)
