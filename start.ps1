# Project Genesis Quick-Start Launcher
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "PROJECT GENESIS - Autonomous AI Society Simulation" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Run automated tests to verify simulation engine
Write-Host "`n[1/3] Running automated tests on all 12 Generative Agent scenarios..." -ForegroundColor Green
$env:PYTHONPATH="backend"
.\.venv\Scripts\pytest backend\tests -q -W ignore::DeprecationWarning
if ($LASTEXITCODE -ne 0) {
    Write-Host "Tests failed! Aborting start." -ForegroundColor Red
    exit 1
}
Write-Host "All automated tests PASSED!" -ForegroundColor Green

# 2. Instructions to run
Write-Host "`n[2/3] Starting Backend API & Simulation Engine on http://localhost:8000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; $env:PYTHONPATH='backend'; .\.venv\Scripts\python run_simulation.py"

# 3. Start Frontend
Write-Host "[3/3] Starting React 19 Frontend Dashboard on http://localhost:5173..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev"

Write-Host "`nProject Genesis is running!" -ForegroundColor Green
Write-Host "Dashboard: http://localhost:5173" -ForegroundColor Yellow
Write-Host "Backend API: http://localhost:8000/docs" -ForegroundColor Yellow
