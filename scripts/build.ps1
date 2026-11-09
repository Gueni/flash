# Full Windows build of Flash: venv -> deps -> tests -> PyInstaller -> smoke test -> portable zip -> Inno Setup installer.
#   powershell -ExecutionPolicy Bypass -File scripts\build.ps1 [-SkipTests] [-OneFile]
#
#   default   : dist\Flash\ (one folder)  ->  release\Flash-<v>-Setup.exe  +  release\Flash-<v>-windows-x64.zip
#   -OneFile  : single portable exe       ->  release\Flash-<v>-windows-x64.exe  (no installer)
param(
    [switch]$SkipTests,
    [switch]$OneFile
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    & (Join-Path $PSScriptRoot "setup_venv.ps1") -Dev
} else {
    Write-Host "==> Installing dependencies" -ForegroundColor Cyan
    & .venv\Scripts\python.exe -m pip install -q -r requirements-dev.txt
    if ($LASTEXITCODE -ne 0) { throw "pip install failed" }
}
$Py = Join-Path $Root ".venv\Scripts\python.exe"
$Version = (& $Py -c "import sys; sys.path.insert(0, 'src'); import flash; print(flash.__version__)").Trim()
Write-Host "==> Flash $Version" -ForegroundColor Cyan

if (-not $SkipTests) {
    Write-Host "==> Running tests" -ForegroundColor Cyan
    & $Py -m unittest tests.test_flash_core tests.test_arduino
    if ($LASTEXITCODE -ne 0) { throw "tests failed" }
}

# arduino-cli for the Code page: downloaded once into vendor\ (checksum-verified) and bundled into the app.
if (-not (Test-Path "vendor\arduino-cli\arduino-cli.exe")) {
    Write-Host "==> Fetching arduino-cli" -ForegroundColor Cyan
    & $Py -c "import sys; sys.path.insert(0, 'src'); from pathlib import Path; from flash.core.arduino import download_cli; print(download_cli(Path('vendor/arduino-cli')))"
    if ($LASTEXITCODE -ne 0) { throw "arduino-cli download failed" }
}

Write-Host "==> Building executable" -ForegroundColor Cyan
if ($OneFile) { $env:FLASH_ONEFILE = "1" } else { Remove-Item Env:FLASH_ONEFILE -ErrorAction SilentlyContinue }
& $Py -m PyInstaller --clean --noconfirm flash.spec
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }
Remove-Item Env:FLASH_ONEFILE -ErrorAction SilentlyContinue

$Exe = if ($OneFile) { "dist\Flash.exe" } else { "dist\Flash\Flash.exe" }

# The bundled esptool must run from inside the exe (frozen builds re-launch themselves with --run-tool).
Write-Host "==> Smoke testing $Exe" -ForegroundColor Cyan
$out = & $Exe --run-tool esptool version 2>&1 | Out-String
if ($out -notmatch "\d+\.\d+") { throw "bundled esptool did not run:`n$out" }
Write-Host ("    bundled esptool " + ($out.Trim() -split "`n")[-1])
if (-not $OneFile) {
    $cli = "dist\Flash\_internal\flash\bin\arduino-cli.exe"
    if (-not (Test-Path $cli)) { throw "arduino-cli was not bundled ($cli missing)" }
    Write-Host ("    bundled arduino-cli " + ((& $cli version) -join " "))
}

New-Item -ItemType Directory -Force release | Out-Null
if ($OneFile) {
    $target = "release\Flash-$Version-windows-x64.exe"
    Copy-Item -Force $Exe $target
    Write-Host "==> Done: $target" -ForegroundColor Green
    exit 0
}

$zip = "release\Flash-$Version-windows-x64.zip"
# .NET zip + retry: right after the smoke test, antivirus or the exiting process can briefly lock files.
Add-Type -AssemblyName System.IO.Compression.FileSystem
for ($try = 1; ; $try++) {
    try {
        if (Test-Path $zip) { Remove-Item -Force $zip }
        [IO.Compression.ZipFile]::CreateFromDirectory((Resolve-Path "dist\Flash").Path, (Join-Path $Root $zip),
            [IO.Compression.CompressionLevel]::Optimal, $true)
        break
    } catch {
        if ($try -ge 5) { throw }
        Start-Sleep -Seconds 2
    }
}
Write-Host "==> Portable: $zip"

$iscc = @("$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe",
          "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
          "$env:ProgramFiles\Inno Setup 6\ISCC.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $iscc) {
    Write-Warning "Inno Setup 6 not found (winget install JRSoftware.InnoSetup). Portable build is in dist\Flash."
    exit 0
}
Write-Host "==> Building installer" -ForegroundColor Cyan
& $iscc /Q "/DAppVersion=$Version" installer\flash.iss
if ($LASTEXITCODE -ne 0) { throw "Inno Setup failed" }
Write-Host "==> Done: release\Flash-$Version-Setup.exe" -ForegroundColor Green
