@echo off
echo ========================================================
echo Installing Gehor Requirements & Dependencies
echo ========================================================
echo.

echo [1/2] Installing Python Backend Packages...
python -m pip install -r "%~dp0requirements.txt"
if %errorlevel% neq 0 (
    echo [ERROR] Python dependencies installation failed.
    pause
    exit /b %errorlevel%
)

echo.
echo [2/2] Checking and Installing Frontend Dependencies (npm)...
where npm >nul 2>nul
if %errorlevel% equ 0 (
    cd /d "%~dp0frontend"
    call npm install
    cd /d "%~dp0"
    echo Frontend dependencies installed successfully.
) else (
    echo [INFO] npm not found in PATH; skipping frontend npm install.
)

echo.
echo ========================================================
echo All Gehor dependencies installed successfully!
echo To run the application, execute: run.bat
echo ========================================================
pause
