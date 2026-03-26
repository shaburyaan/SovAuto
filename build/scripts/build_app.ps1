Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$distDir = Join-Path $repoRoot "dist\SovAuto"
$buildDir = Join-Path $repoRoot "build\sovauto"
$specPath = Join-Path $repoRoot "sovauto.spec"
$brandingDir = Join-Path $repoRoot "build\branding"
$logoPath = Join-Path $brandingDir "sovauto-logo.png"
$iconPath = Join-Path $brandingDir "sovauto.ico"
$tesseractRoot = if ($env:SOVAUTO_TESSERACT_ROOT) {
    $env:SOVAUTO_TESSERACT_ROOT
} elseif (Test-Path "C:\Program Files\Tesseract-OCR\tesseract.exe") {
    "C:\Program Files\Tesseract-OCR"
} elseif (Test-Path "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe") {
    "C:\Program Files (x86)\Tesseract-OCR"
} else {
    $null
}

Write-Host "==> SovAuto build started"
Push-Location $repoRoot
try {
    Write-Host "==> Installing build dependencies"
    python -m pip install -e ".[dev]"

    if (-not (Test-Path $logoPath)) {
        throw "Branding logo was not found: $logoPath"
    }
    if (-not (Test-Path $iconPath)) {
        throw "Branding icon was not found: $iconPath"
    }

    if (Test-Path $buildDir) {
        Remove-Item $buildDir -Recurse -Force
    }
    if (Test-Path $distDir) {
        Remove-Item $distDir -Recurse -Force
    }

    Write-Host "==> Running PyInstaller"
    python -m PyInstaller $specPath --noconfirm --clean
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller build failed with exit code $LASTEXITCODE"
    }

    $exePath = Join-Path $distDir "SovAuto.exe"
    if (-not (Test-Path $exePath)) {
        throw "Missing packaged executable: $exePath"
    }

    if (-not $tesseractRoot) {
        throw "Tesseract runtime was not found. Install Tesseract OCR or set SOVAUTO_TESSERACT_ROOT."
    }

    $targetTesseractDir = Join-Path $distDir "tesseract"
    if (Test-Path $targetTesseractDir) {
        Remove-Item $targetTesseractDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $targetTesseractDir -Force | Out-Null
    Copy-Item (Join-Path $tesseractRoot "*") $targetTesseractDir -Recurse -Force

    $tesseractExe = Join-Path $targetTesseractDir "tesseract.exe"
    $tessdataDir = Join-Path $targetTesseractDir "tessdata"
    if (-not (Test-Path $tesseractExe)) {
        throw "Bundled Tesseract executable is missing: $tesseractExe"
    }
    if (-not (Test-Path $tessdataDir)) {
        throw "Bundled tessdata directory is missing: $tessdataDir"
    }

    Write-Host "==> SovAuto build completed: $exePath"
} finally {
    Pop-Location
}
