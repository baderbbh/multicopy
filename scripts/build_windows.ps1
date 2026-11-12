$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
$python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Create the virtual environment first: python -m venv .venv"
}
& $python -m pip install -r requirements-dev.txt
if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }
& $python -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw "Tests failed." }
& $python -m PyInstaller --noconfirm --clean --onefile --windowed --name MultiCopy --paths . --add-data "src/assets/multicopy-logo.png;src/assets" run.py
if ($LASTEXITCODE -ne 0) { throw "Build failed." }
Write-Host "Build created: dist\MultiCopy.exe"
