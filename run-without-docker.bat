@echo off
echo 🚀 Starting Volunteer Matching System (Manual Mode)
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed or not in PATH  
    echo Please install Node.js 16+ from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo ✅ Python and Node.js are installed
echo.

REM Set environment variables
set MONGODB_URL=mongodb+srv://aivolunteer:aRZH1TmJP65LfXCe@cluster0.mqjdi.mongodb.net/?retryWrites=true^&w=majority^&appName=Cluster0
set OPENAI_API_KEY=sk-proj-KzfYmFuHvV2-wQxVtGt0wKLdyMf9Bf_5WPYb8U3OW-5TG6kN8vLJ2WUQFdT5hSTdPM2KqWtT3BlbkFJlOEWvNYcRr1sOPfhJKx9JZiPe3rKvM1cFGk7_YWQJ1OdFbMq6rBvS8hKy
set JWT_SECRET_KEY=volunteer-matching-super-secret-jwt-key-2024
set ENVIRONMENT=development
set LOG_LEVEL=INFO

echo 🔧 Environment variables set
echo.

REM Backend Setup
echo 📦 Setting up Backend...
cd backend

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt >nul 2>&1

REM Download NLTK data
echo Downloading NLTK data...
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('vader_lexicon', quiet=True)" >nul 2>&1

echo ✅ Backend setup complete
echo.

REM Start backend in background
echo 🚀 Starting Backend Server...
start "Backend Server" cmd /k "venv\Scripts\activate && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Give backend time to start
timeout /t 5 >nul

REM Frontend Setup
echo 📦 Setting up Frontend...
cd ..\frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing Node.js dependencies...
    npm install
) else (
    echo Node.js dependencies already installed
)

echo ✅ Frontend setup complete
echo.

REM Start frontend
echo 🚀 Starting Frontend Server...
start "Frontend Server" cmd /k "npm start"

echo.
echo 🎉 System Starting!
echo.
echo ⏰ Please wait 30-60 seconds for services to start...
echo.
echo 🌐 Access points:
echo   Frontend: http://localhost:3000
echo   Backend API: http://localhost:8000  
echo   API Docs: http://localhost:8000/docs
echo.
echo 📝 Logs will appear in the opened terminal windows
echo 🛑 To stop: Close both terminal windows or press Ctrl+C in each
echo.

REM Wait a bit and try to open the application
timeout /t 10 >nul
echo 🔗 Opening application in browser...
start http://localhost:3000

echo.
echo ✅ System started successfully!
echo Check the opened terminal windows for any error messages.
echo.
pause 