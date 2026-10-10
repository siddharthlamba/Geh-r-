Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Installing Gehor Requirements & Dependencies" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/2] Installing Python Backend Packages..." -ForegroundColor Green
python -m pip install -r "$PSScriptRoot\requirements.txt"

Write-Host ""
Write-Host "[2/2] Checking and Installing Frontend Dependencies (npm)..." -ForegroundColor Green
if (Get-Command npm -ErrorAction SilentlyContinue) {
    Push-Location "$PSScriptRoot\frontend"
    npm install
    Pop-Location
    Write-Host "Frontend dependencies installed successfully." -ForegroundColor Green
} else {
    Write-Host "[INFO] npm not found in PATH; skipping frontend npm install." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "All Gehor dependencies installed successfully!" -ForegroundColor Green
Write-Host "To run the application, execute: .\run.bat" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
