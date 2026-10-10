@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo Checking Docker Engine...
docker info >nul 2>&1
if errorlevel 1 (
  echo.
  echo ERROR: Docker Engine is not available.
  echo Start Docker Desktop, wait until it is ready, and run start.bat again.
  echo.
  pause
  exit /b 1
)

docker compose version >nul 2>&1
if errorlevel 1 (
  echo.
  echo ERROR: The "docker compose" command is not available.
  echo Install or update Docker Desktop and run start.bat again.
  echo.
  pause
  exit /b 1
)

if not exist ".env" (
  echo Creating local configuration...
  powershell -NoProfile -Command "$bytes = New-Object byte[] 32; $rng = New-Object Security.Cryptography.RNGCryptoServiceProvider; $rng.GetBytes($bytes); $rng.Dispose(); $secret = ([BitConverter]::ToString($bytes)).Replace('-', ''); 'CNK_ADMIN_PASSWORD=' + $secret | Set-Content -Encoding ascii '.env'"
  if errorlevel 1 (
    echo.
    echo ERROR: Could not create the local .env configuration.
    echo Create .env manually using .env.example and try again.
    echo.
    pause
    exit /b 1
  )
)

echo Building and starting Cloud Native Kosice...
docker compose up -d --build
if errorlevel 1 (
  echo.
  echo ERROR: Docker Compose could not start the application.
  echo Review the messages above or run: docker compose logs
  echo.
  pause
  exit /b 1
)

echo Waiting for the application to become ready...
for /L %%I in (1,1,60) do (
  curl.exe -fsS "http://localhost:3001/api/health" >nul 2>&1
  if not errorlevel 1 (
    curl.exe -fsS "http://localhost:8080/" >nul 2>&1
    if not errorlevel 1 goto ready
  )
  powershell -NoProfile -Command "Start-Sleep -Seconds 2"
)

echo.
echo ERROR: The application did not become ready within 120 seconds.
echo Container status:
docker compose ps
echo.
echo Recent logs:
docker compose logs --tail 40
echo.
pause
exit /b 1

:ready
echo Application is ready at http://localhost:8080/
start "" "http://localhost:8080/"
exit /b 0
