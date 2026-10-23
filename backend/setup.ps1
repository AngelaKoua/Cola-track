# CTrack Backend Setup Script
# This script helps you set up the backend environment

Write-Host "🚀 CTrack Backend Setup" -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "📋 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.10 or higher from https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

# Check PostgreSQL
Write-Host ""
Write-Host "📋 Checking PostgreSQL installation..." -ForegroundColor Yellow
try {
    $pgVersion = psql --version 2>&1
    Write-Host "✅ $pgVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠️  PostgreSQL command line tools not found in PATH" -ForegroundColor Yellow
    Write-Host "Please ensure PostgreSQL is installed and configured" -ForegroundColor Yellow
}

# Create virtual environment
Write-Host ""
Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "⚠️  Virtual environment already exists" -ForegroundColor Yellow
    $response = Read-Host "Do you want to recreate it? (y/n)"
    if ($response -eq "y") {
        Remove-Item -Recurse -Force .venv
        python -m venv .venv
        Write-Host "✅ Virtual environment recreated" -ForegroundColor Green
    }
} else {
    python -m venv .venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1
Write-Host "✅ Virtual environment activated" -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "✅ Dependencies installed" -ForegroundColor Green

# Create .env file
Write-Host ""
Write-Host "⚙️  Configuring environment variables..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "⚠️  .env file already exists" -ForegroundColor Yellow
} else {
    Copy-Item env.example .env
    Write-Host "✅ .env file created from template" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Please edit .env file and update:" -ForegroundColor Yellow
    Write-Host "   - DATABASE_URL with your PostgreSQL credentials" -ForegroundColor Yellow
    Write-Host "   - SECRET_KEY with a secure random key" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Generate a secure SECRET_KEY with:" -ForegroundColor Cyan
    Write-Host "   python -c 'import secrets; print(secrets.token_hex(32))'" -ForegroundColor White
}

# Database setup instructions
Write-Host ""
Write-Host "🗄️  Database Setup Instructions:" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Connect to PostgreSQL:" -ForegroundColor Yellow
Write-Host "   psql -U postgres" -ForegroundColor White
Write-Host ""
Write-Host "2. Create database:" -ForegroundColor Yellow
Write-Host "   CREATE DATABASE ctrack_db;" -ForegroundColor White
Write-Host ""
Write-Host "3. (Optional) Create user:" -ForegroundColor Yellow
Write-Host "   CREATE USER ctrack_user WITH PASSWORD 'your_password';" -ForegroundColor White
Write-Host "   GRANT ALL PRIVILEGES ON DATABASE ctrack_db TO ctrack_user;" -ForegroundColor White
Write-Host ""
Write-Host "4. Update DATABASE_URL in .env file" -ForegroundColor Yellow
Write-Host ""

# Next steps
Write-Host ""
Write-Host "✨ Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next Steps:" -ForegroundColor Cyan
Write-Host "=============" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Edit .env file with your database credentials" -ForegroundColor Yellow
Write-Host "2. Create the PostgreSQL database (see instructions above)" -ForegroundColor Yellow
Write-Host "3. Run the application:" -ForegroundColor Yellow
Write-Host "   uvicorn app.main:app --reload" -ForegroundColor White
Write-Host ""
Write-Host "4. Visit the API documentation:" -ForegroundColor Yellow
Write-Host "   http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Happy coding! 🎉" -ForegroundColor Green
