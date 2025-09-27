@echo off
echo 🐳 Docker Desktop Installation Helper
echo.

echo This script will help you install Docker Desktop for Windows
echo.

echo 📋 Prerequisites Check:
echo.

REM Check Windows version
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j
echo Windows Version: %VERSION%

REM Check if running on Windows 10/11
if "%VERSION%" lss "10.0" (
    echo ❌ Docker Desktop requires Windows 10 or later
    echo Please upgrade your Windows version
    pause
    exit /b 1
)

echo ✅ Windows version is compatible
echo.

REM Check if WSL is available (Windows 10 version 2004 and higher)
wsl --list >nul 2>&1
if errorlevel 1 (
    echo ⚠️  WSL (Windows Subsystem for Linux) is not installed
    echo Docker Desktop works better with WSL 2
    echo.
    echo Would you like to install WSL 2? (recommended)
    echo.
    set /p choice="Install WSL 2? (y/n): "
    if /i "%choice%"=="y" (
        echo Installing WSL 2...
        dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
        dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
        echo.
        echo ⚠️  A restart is required to complete WSL installation
        echo After restart, run this script again to continue Docker installation
        echo.
        set /p restart="Restart now? (y/n): "
        if /i "%restart%"=="y" (
            shutdown /r /t 5
            exit /b 0
        )
    )
) else (
    echo ✅ WSL is installed
)

echo.
echo 🔄 Starting Docker Desktop installation...
echo.

REM Create temp directory
if not exist "%TEMP%\docker-install" mkdir "%TEMP%\docker-install"
cd /d "%TEMP%\docker-install"

echo 📥 Downloading Docker Desktop...
echo This may take a few minutes depending on your internet speed...
echo.

REM Download Docker Desktop using PowerShell
powershell -Command "& {Invoke-WebRequest -Uri 'https://desktop.docker.com/win/main/amd64/Docker Desktop Installer.exe' -OutFile 'DockerDesktopInstaller.exe'}"

if not exist "DockerDesktopInstaller.exe" (
    echo ❌ Download failed! 
    echo.
    echo Please manually download Docker Desktop from:
    echo https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

echo ✅ Download completed!
echo.

echo 🚀 Starting Docker Desktop installation...
echo.
echo ⚠️  Important notes:
echo   - The installer may require administrator privileges
echo   - You may need to restart your computer
echo   - The installation process may take several minutes
echo.

set /p proceed="Proceed with installation? (y/n): "
if /i "%proceed%"=="y" (
    echo Starting installer...
    start "" "DockerDesktopInstaller.exe" install --quiet
    echo.
    echo 📦 Docker Desktop installer is running...
    echo.
    echo Next steps after installation:
    echo 1. Restart your computer if prompted
    echo 2. Start Docker Desktop from the Start Menu
    echo 3. Wait for Docker to finish starting (whale icon in system tray)
    echo 4. Run 'docker --version' to verify installation
    echo 5. Use docker-compose to start the Volunteer Matching System
    echo.
) else (
    echo Installation cancelled.
    echo.
    echo To install manually:
    echo 1. Go to https://www.docker.com/products/docker-desktop
    echo 2. Download Docker Desktop for Windows
    echo 3. Run the installer as administrator
    echo.
)

echo.
echo 📋 Alternative: Manual Installation Steps
echo.
echo If the automatic installation doesn't work:
echo.
echo 1. Visit: https://www.docker.com/products/docker-desktop
echo 2. Click "Download for Windows"
echo 3. Run "Docker Desktop Installer.exe" as administrator
echo 4. Follow the installation wizard
echo 5. Restart computer when prompted
echo 6. Start Docker Desktop from Start Menu
echo 7. Wait for Docker whale icon to appear in system tray
echo 8. Open terminal and run: docker --version
echo.

echo 🆘 If you have issues:
echo.
echo Common solutions:
echo - Enable Virtualization in BIOS
echo - Install Windows updates
echo - Run as administrator
echo - Temporarily disable antivirus during installation
echo.

pause

REM Clean up
cd /d "%~dp0"
rmdir /s /q "%TEMP%\docker-install" 2>nul 