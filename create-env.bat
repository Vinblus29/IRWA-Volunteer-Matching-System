@echo off
echo Creating .env files for Volunteer Matching System...

echo.
echo Creating backend/.env file...
copy backend\env.config backend\.env
echo Backend .env file created successfully!

echo.
echo Creating frontend/.env file...
copy frontend\env.config frontend\.env  
echo Frontend .env file created successfully!

echo.
echo ✅ Environment files created successfully!
echo.
echo Next steps:
echo 1. Review backend/.env and update any credentials if needed
echo 2. Review frontend/.env and update API URL if needed
echo 3. Run: docker-compose up --build
echo.
pause 