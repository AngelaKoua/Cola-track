# CTrack Backend API

Professional FastAPI backend for the CTrack industrial monitoring system. This API manages data for two industrial machines: **Osmoseur** (reverse osmosis water treatment) and **Remplisseuse** (bottle filling machine).

## 🚀 Features

- **RESTful API** with FastAPI
- **PostgreSQL Database** with SQLAlchemy ORM
- **JWT Authentication** for secure access
- **CORS Support** for Next.js frontend integration
- **Rate Limiting** to prevent API abuse
- **Pagination & Sorting** for efficient data retrieval
- **Data Validation** with Pydantic schemas
- **Database Migrations** with Alembic
- **Comprehensive API Documentation** (Swagger UI & ReDoc)
- **Type Safety** with Python type hints

## 📋 Prerequisites

- Python 3.10 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

## 🛠️ Installation

### 1. Clone the Repository

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure PostgreSQL Database

Create a new PostgreSQL database:

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE ctrack_db;

-- Create user (optional)
CREATE USER ctrack_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ctrack_db TO ctrack_user;
```

### 5. Configure Environment Variables

Copy the example environment file and update it with your settings:

```bash
# Windows
copy env.example .env

# Linux/Mac
cp env.example .env
```

Edit `.env` file:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/ctrack_db

# API Configuration
API_V1_PREFIX=/api
PROJECT_NAME=CTrack API
DEBUG=True

# CORS Configuration (Next.js frontend)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# JWT Authentication
# Generate with: openssl rand -hex 32
SECRET_KEY=your-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

### 6. Initialize Database

#### Option A: Using Alembic Migrations (Recommended)

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

#### Option B: Direct Table Creation (Development Only)

The tables will be created automatically when you run the application in DEBUG mode.

## 🏃 Running the Application

### Development Mode

```bash
# Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python -m app.main
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Production Mode

```bash
# Set DEBUG=False in .env first
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📚 API Documentation

### Interactive Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs (interactive API testing)
- **ReDoc**: http://localhost:8000/redoc (clean API documentation)

### API Endpoints

#### Osmoseur Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/osmoseur` | Create new record |
| GET | `/api/osmoseur` | List all records (paginated) |
| GET | `/api/osmoseur/{id}` | Get single record |
| PUT | `/api/osmoseur/{id}` | Update record |
| DELETE | `/api/osmoseur/{id}` | Delete record |
| GET | `/api/osmoseur/latest` | Get most recent record |
| GET | `/api/osmoseur/stats` | Get statistical summary |

#### Remplisseuse Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/remplisseuse` | Create new record |
| GET | `/api/remplisseuse` | List all records (paginated) |
| GET | `/api/remplisseuse/{id}` | Get single record |
| PUT | `/api/remplisseuse/{id}` | Update record |
| DELETE | `/api/remplisseuse/{id}` | Delete record |
| GET | `/api/remplisseuse/latest` | Get most recent record |
| GET | `/api/remplisseuse/stats` | Get statistical summary |

### Example Requests

#### Create Osmoseur Record

```bash
curl -X POST "http://localhost:8000/api/osmoseur" \
  -H "Content-Type: application/json" \
  -d '{
    "debit_permeat": 15000,
    "debit_concentrat": 5000,
    "taux_recuperation": 75.0,
    "conductivite_permeat": 15.0,
    "ph_entree": 7.2,
    "ph_sortie": 6.8,
    "turbidite": 0.5,
    "chlore_libre": 0.1,
    "durete_totale": 0.0,
    "tds": 10.0
  }'
```

#### Get Paginated Records

```bash
curl "http://localhost:8000/api/osmoseur?page=1&page_size=20&sort_by=created_at&sort_order=desc"
```

## 🗄️ Database Schema

### Osmoseur Table

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| debit_permeat | Float | Permeate flow rate (L/h) |
| debit_concentrat | Float | Concentrate flow rate (L/h) |
| taux_recuperation | Float | Recovery rate (%) |
| conductivite_permeat | Float | Permeate conductivity (µS/cm) |
| ph_entree | Float | Inlet pH |
| ph_sortie | Float | Outlet pH |
| turbidite | Float | Turbidity (NTU) |
| chlore_libre | Float | Free chlorine (mg/L) |
| durete_totale | Float | Total hardness (°f) |
| tds | Float | Total Dissolved Solids (ppm) |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

### Remplisseuse Table

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| temperature_remplissage | Float | Filling temperature (°C) |
| volume_remplissage | Float | Fill volume (L) |
| carbonation | Float | CO₂ level (g/L) |
| mtbf | Float | Mean Time Between Failures (h) |
| rendement | Float | Production efficiency (%) |
| conso_air_co2 | Float | Air/CO₂ consumption (m³/h) |
| vibrations | Float | Motor vibrations (mm/s) |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

## 🧪 Testing

The `tests/` folder holds manual check scripts (most of them need the API
running on `localhost:8000` and/or a seeded database). Run them from the
`backend/` directory as modules so that `app` can be imported:

```bash
# Example: end-to-end incident flow (FastAPI TestClient)
python -m tests.test_incident_flow

# Example: AI chat endpoint (API must be running)
python -m tests.test_expert
```

## 🔧 Development

### Project Structure

```text
backend/
├── app/                     # FastAPI application
│   ├── main.py              # Entry point (routers, CORS, background jobs)
│   ├── config.py            # Settings loaded from .env
│   ├── database.py          # SQLAlchemy engine & sessions
│   ├── models/              # SQLAlchemy models (DB tables)
│   ├── schemas/             # Pydantic schemas (request/response validation)
│   ├── routers/             # API endpoints
│   ├── services/            # Business logic
│   │   └── ai/              # 5-layer AI engine + Gemini chatbot
│   ├── repositories/        # Data access layer (telemetry)
│   ├── jobs/                # Background workers (ML inference every 5 min)
│   ├── ml_models/           # Trained ML models (.joblib) — written by data-science/train_models.py
│   └── utils/
├── analytics/               # BI endpoints (/analytics) on the data warehouse
├── datawarehouse/           # ETL + star schema (dw_schema.sql)
├── alembic/                 # Database migrations
├── scripts/                 # One-off utility scripts (run with `python -m scripts.<folder>.<name>`)
│   ├── seed/                # Populate the database (users, machine data)
│   ├── db/                  # Inspect / migrate / reset the database
│   ├── etl/                 # Run and verify the data warehouse ETL
│   └── debug/               # Debugging helpers
├── tests/                   # Manual check scripts
├── env.example              # Environment template (copy to .env)
├── requirements.txt         # Python dependencies
├── setup.ps1                # Automated setup (Windows)
└── README.md                # This file
```

### Code Style

This project follows PEP 8 style guidelines. Format code with:

```bash
# Format with black
black app/

# Lint with flake8
flake8 app/
```

## 🔐 Security

- **JWT Authentication**: Secure token-based authentication
- **Rate Limiting**: 60 requests per minute per IP
- **CORS**: Configured for specific origins only
- **Input Validation**: Pydantic schemas validate all inputs
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | - |
| API_V1_PREFIX | API route prefix | /api |
| PROJECT_NAME | Project name for docs | CTrack API |
| DEBUG | Enable debug mode | True |
| CORS_ORIGINS | Allowed CORS origins | localhost:3000 |
| SECRET_KEY | JWT secret key | - |
| ALGORITHM | JWT algorithm | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token expiration | 30 |
| RATE_LIMIT_PER_MINUTE | Rate limit | 60 |

## 🚀 Deployment

### Using Docker (Coming Soon)

```bash
docker build -t ctrack-api .
docker run -p 8000:8000 ctrack-api
```

### Manual Deployment

1. Set `DEBUG=False` in `.env`
2. Generate a secure `SECRET_KEY`
3. Use a production WSGI server (Gunicorn + Uvicorn)
4. Set up PostgreSQL with proper credentials
5. Configure HTTPS/SSL
6. Set up proper logging
7. Configure database backups

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Run tests
4. Submit a pull request

## 📄 License

This project is proprietary software for CTrack industrial monitoring.

## 👥 Authors

- Development Team - CTrack Project

## 📞 Support

For support, please contact the development team.
