@echo off
setlocal

echo ==========================================
echo   GEO ACCESSIBILITY - DOCKER APP START
echo ==========================================
echo.

echo Building and starting database + dashboard...
docker compose --env-file .env -f docker/docker-compose.yml up --build -d

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to start Docker app.
    pause
    exit /b %errorlevel%
)

echo.
echo ==========================================
echo   APP IS READY
echo   Dashboard: http://localhost:8050
echo ==========================================
echo.

pause