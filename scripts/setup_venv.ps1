# Create .venv and install Flash's dependencies (Windows PowerShell).
#   powershell -ExecutionPolicy Bypass -File scripts\setup_venv.ps1 [-Dev] [-Python <path>]
param(
    [switch]$Dev,
    [string]$Python = ""
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not $Python) {
    if (Get-Command py -ErrorAction SilentlyContinue) { $Python = "py" }
    elseif (Get-Command python -ErrorAction SilentlyContinue) { $Python = "python" }
    else { throw "Python 3.10+ not found. Install it from https://www.python.org/downloads/" }
}

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Creating virtual environment in .venv ..." -ForegroundColor Cyan
    if ($Python -eq "py") { & py -3 -m venv .venv } else { & $Python -m venv .venv }
    if ($LASTEXITCODE -ne 0) { throw "venv creation failed" }
}
$Py = Join-Path $Root ".venv\Scripts\python.exe"

& $Py -m pip install --upgrade pip
# The wrong 'serial' package breaks pyserial ("module 'serial' has no attribute 'Serial'").
& $Py -m pip uninstall -y serial 2>$null | Out-Null
$req = if ($Dev) { "requirements-dev.txt" } else { "requirements.txt" }
& $Py -m pip install -r $req
if ($LASTEXITCODE -ne 0) { throw "pip install failed" }

Write-Host ""
Write-Host "Done. Run the app with:  .venv\Scripts\python.exe main.py" -ForegroundColor Green
