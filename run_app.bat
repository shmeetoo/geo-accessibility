@echo off
setlocal

echo ==========================================
echo   GEO ACCESSIBILITY - DOCKER APP START
echo ==========================================
echo.

echo Building and starting database + dashboard...
docker compose --env-file .env.docker -f docker/docker-compose.yml up -d
@REM add --build after code changes

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to start Docker app.
    pause
    exit /b %errorlevel%
)

echo.
echo Waiting for app to be ready...

:wait_loop
curl -s http://localhost:8050/_dash-layout >nul
if %errorlevel% neq 0 (
    timeout /t 2 >nul
    goto wait_loop
)

echo.
echo ==========================================
echo   APP IS READY
echo   Dashboard: http://localhost:8050
echo ==========================================
echo.

pause