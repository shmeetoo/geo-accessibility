@echo off
REM -------------------------------
REM Interaktywny kontroler Docker Compose
REM -------------------------------

set COMPOSE_FILE=docker/docker-compose.yml
set ENV_FILE=.env
set PROJECT_NAME=geo_postgres

:MENU
cls
echo ================================
echo   Docker Compose Control Panel
echo ================================
echo.
echo 1. Start container
echo 2. Stop container
echo 3. Restart container
echo 4. Clean container
echo 5. Exit
echo.
set /p choice="Choose action [1-5]: "

if "%choice%"=="1" goto START
if "%choice%"=="2" goto STOP
if "%choice%"=="3" goto RESTART
if "%choice%"=="4" goto CLEAN
if "%choice%"=="5" goto END
echo Wrong choice!
pause
goto MENU

:START
docker compose --env-file %ENV_FILE% -p %PROJECT_NAME% -f %COMPOSE_FILE% up -d
echo Containers running.
pause
goto MENU

:STOP
docker compose --env-file %ENV_FILE% -p %PROJECT_NAME% -f %COMPOSE_FILE% stop
echo Containers stopped.
pause
goto MENU

:RESTART
docker compose --env-file %ENV_FILE% -p %PROJECT_NAME% -f %COMPOSE_FILE% stop
docker compose --env-file %ENV_FILE% -p %PROJECT_NAME% -f %COMPOSE_FILE% start
echo Containers restarted.
pause
goto MENU

:CLEAN
docker compose --env-file %ENV_FILE% -p %PROJECT_NAME% -f %COMPOSE_FILE% down
echo Containers cleaned.
pause
goto MENU

:END
pause