@echo off
title Volunteer Matching System - Startup
color 0A

echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║           🤝 INTELLIGENT VOLUNTEER MATCHING SYSTEM           ║
echo  ║                                                              ║
echo  ║  🤖 Multi-Agent AI System                                    ║
echo  ║  🧠 LLM Integration (OpenAI GPT)                             ║
echo  ║  🔤 NLP Processing (spaCy, NLTK)                             ║
echo  ║  🔍 Information Retrieval (ChromaDB)                         ║
echo  ║  🔐 Enterprise Security (JWT, Encryption)                    ║
echo  ║  ⚖️  Responsible AI (Fairness, Explainability)               ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

echo 🚀 Starting system initialization...
echo.

REM Check if Docker is available
docker --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Docker is not installed or not running
    echo.
    echo Choose startup method:
    echo.
    echo [1] Install Docker Desktop (recommended)
    echo [2] Run without Docker (manual mode)
    echo [3] Exit
    echo.
    set /p method="Enter choice (1-3): "
    
    if "%method%"=="1" (
        echo.
        echo 🐳 Starting Docker installation...
        call install-docker.bat
        echo.
        echo After Docker installation completes, run this script again.
        pause
        exit /b 0
    )
    
    if "%method%"=="2" (
        echo.
        echo 🔧 Starting in manual mode...
        call run-without-docker.bat
        exit /b 0
    )
    
    if "%method%"=="3" (
        echo Goodbye!
        pause
        exit /b 0
    )
    
    echo Invalid choice. Defaulting to manual mode...
    call run-without-docker.bat
    exit /b 0
)

REM Docker is available
echo ✅ Docker is installed!
echo.

REM Check if Docker Desktop is running
docker ps >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Docker Desktop is not running
    echo.
    echo Please start Docker Desktop and wait for it to fully load
    echo (Look for the whale icon in your system tray)
    echo.
    echo Choose an option:
    echo [1] Wait and retry Docker
    echo [2] Run without Docker (manual mode) 
    echo [3] Exit
    echo.
    set /p choice="Enter choice (1-3): "
    
    if "%choice%"=="1" (
        echo.
        echo ⏳ Waiting for Docker Desktop to start...
        echo Press any key once Docker Desktop is running...
        pause >nul
        goto :docker_check
    )
    
    if "%choice%"=="2" (
        echo.
        echo 🔧 Starting in manual mode...
        call run-without-docker.bat
        exit /b 0
    )
    
    if "%choice%"=="3" (
        echo Goodbye!
        pause
        exit /b 0
    )
)

:docker_check
docker ps >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is still not responding
    echo.
    echo Fallback: Starting in manual mode...
    call run-without-docker.bat
    exit /b 0
)

echo ✅ Docker Desktop is running!
echo.

REM Check if .env files exist
if not exist "backend\.env" (
    echo 📝 Creating environment files...
    call create-env.bat >nul
    echo ✅ Environment files created
    echo.
)

REM Set OpenAI API key if not set
if "%OPENAI_API_KEY%"=="" (
    set OPENAI_API_KEY=sk-proj-KzfYmFuHvV2-wQxVtGt0wKLdyMf9Bf_5WPYb8U3OW-5TG6kN8vLJ2WUQFdT5hSTdPM2KqWtT3BlbkFJlOEWvNYcRr1sOPfhJKx9JZiPe3rKvM1cFGk7_YWQJ1OdFbMq6rBvS8hKy
    echo 🔑 OpenAI API key configured
)

echo 🐳 Starting with Docker Compose...
echo.

REM Stop any existing containers
docker-compose down >nul 2>&1

echo 📦 Building and starting services...
echo This may take 5-10 minutes on first run...
echo.

REM Start the system
docker-compose up --build -d

if errorlevel 1 (
    echo ❌ Docker Compose failed to start
    echo.
    echo Fallback: Starting in manual mode...
    call run-without-docker.bat
    exit /b 0
)

echo ✅ Services starting...
echo.

REM Wait for services to be ready
echo ⏳ Waiting for services to initialize...
timeout /t 30 >nul

echo.
echo 🎉 SYSTEM STARTED SUCCESSFULLY!
echo.
echo 🌐 Access Points:
echo   📱 Frontend:     http://localhost:3000
echo   🔗 Backend API:  http://localhost:8000
echo   📚 API Docs:     http://localhost:8000/docs
echo   💾 Redis:        localhost:6379
echo.
echo 📊 Service Status:
docker-compose ps

echo.
echo 📝 Useful Commands:
echo   📋 View logs:        docker-compose logs -f
echo   🔄 Restart:          docker-compose restart
echo   🛑 Stop:             docker-compose down
echo   🔧 Rebuild:          docker-compose up --build
echo.

REM Open the application
echo 🔗 Opening application in browser...
start http://localhost:3000

echo.
echo ✅ System is ready! Check browser for the application.
echo.
echo Press any key to view logs (Ctrl+C to exit logs)...
pause >nul

docker-compose logs -f 