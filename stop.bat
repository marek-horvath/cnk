@echo off
setlocal EnableExtensions
cd /d "%~dp0"

docker info >nul 2>&1
if errorlevel 1 (
  echo.
  echo ERROR: Docker Engine is not available.
  echo Start Docker Desktop and run stop.bat again.
  echo.
  pause
  exit /b 1
)

echo Stopping Cloud Native Kosice...
docker compose down
if errorlevel 1 (
  echo.
  echo ERROR: The application could not be stopped cleanly.
  echo.
  pause
  exit /b 1
)

echo Application stopped. Stored data was preserved.
exit /b 0
