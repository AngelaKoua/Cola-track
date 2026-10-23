# 🚀 Quick Start Guide - CTrack Backend

This guide will get you up and running with the CTrack backend API in minutes.

## Prerequisites Checklist

- [ ] Python 3.10+ installed
- [ ] PostgreSQL 12+ installed and running
- [ ] Git installed (optional)

## Step-by-Step Setup

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Run Setup Script (Automated)

```powershell
# Run the automated setup script
.\setup.ps1
```

This script will:
- ✅ Check Python installation
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Create .env file from template

### 3. Configure Database

#### Option A: Using PostgreSQL Command Line

```bash
# Open PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE ctrack_db;

# Exit
\q
```

#### Option B: Using pgAdmin

1. Open pgAdmin
2. Right-click on "Databases"
3. Create > Database
4. Name: `ctrack_db`
5. Click "Save"

### 4. Update Environment Variables

Edit the `.env` file in the `backend/` directory:

```env
# Update this line with your PostgreSQL password
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD_HERE@localhost:5432/ctrack_db

# Generate a secure secret key (see below)
SECRET_KEY=your-generated-secret-key-here
```

**Generate a secure SECRET_KEY:**

```bash
# Activate virtual environment first
.\.venv\Scripts\activate

# Generate key
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste it as your `SECRET_KEY` in `.env`

### 5. Run the Application

```bash
# Make sure virtual environment is activated
.\.venv\Scripts\activate

# Start the server
uvicorn app.main:app --reload
```

You should see:

```
🚀 Starting CTrack API...
📊 Database: localhost:5432/ctrack_db
⚠️  DEBUG MODE: Creating database tables...
✅ Database tables created
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 6. Test the API

Open your browser and visit:

- **Swagger UI (Interactive API Docs)**: http://localhost:8000/docs
- **ReDoc (Clean Documentation)**: http://localhost:8000/redoc
- **API Root**: http://localhost:8000

## 🎯 Quick API Test

### Using Swagger UI (Recommended for Beginners)

1. Go to http://localhost:8000/docs
2. Click on `POST /api/osmoseur`
3. Click "Try it out"
4. Use this example data:

```json
{
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
}
```

5. Click "Execute"
6. You should see a `201 Created` response!

### Using cURL

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

## 🔍 Verify Database

Check that data was saved to PostgreSQL:

```sql
-- Connect to database
psql -U postgres -d ctrack_db

-- View all osmoseur records
SELECT * FROM osmoseur;

-- View all remplisseuse records
SELECT * FROM remplisseuse;
```

## 🛠️ Common Issues & Solutions

### Issue: "ModuleNotFoundError"

**Solution:** Make sure virtual environment is activated:

```bash
.\.venv\Scripts\activate
```

### Issue: "Could not connect to database"

**Solutions:**
1. Check PostgreSQL is running
2. Verify DATABASE_URL in `.env` is correct
3. Ensure database `ctrack_db` exists
4. Check username/password are correct

### Issue: "Port 8000 already in use"

**Solution:** Use a different port:

```bash
uvicorn app.main:app --reload --port 8001
```

### Issue: "CORS error" when connecting from frontend

**Solution:** Add your frontend URL to CORS_ORIGINS in `.env`:

```env
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## 📚 Next Steps

1. ✅ API is running
2. ✅ Database is connected
3. ✅ Test endpoints work

**Now you can:**

- Explore all endpoints in Swagger UI
- Integrate with your Next.js frontend
- Create more test data
- View statistics at `/api/osmoseur/stats`

## 🎓 Learning Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLAlchemy Tutorial**: https://docs.sqlalchemy.org/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

## 💡 Tips

- Use Swagger UI for testing - it's interactive and easy!
- Check the terminal for helpful debug messages
- Database tables are created automatically in DEBUG mode
- All API responses include helpful error messages

## 🆘 Need Help?

Check the full README.md for detailed documentation and troubleshooting.

---

**Happy coding! 🎉**
