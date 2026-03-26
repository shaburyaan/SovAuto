Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$isccPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
$issPath = Join-Path $repoRoot "SovAuto.iss"
$versionFile = Join-Path $repoRoot "build\version\version.txt"
$distAppPath = Join-Path $repoRoot "dist\SovAuto\SovAuto.exe"
$brandingDir = Join-Path $repoRoot "build\branding"
$installerBranding = @(
    (Join-Path $brandingDir "sovauto.ico"),
    (Join-Path $brandingDir "wizard-image.bmp"),
    (Join-Path $brandingDir "wizard-small.bmp")
)

if (-not (Test-Path $isccPath)) {
    throw "Inno Setup compiler was not found: $isccPath"
}
if (-not (Test-Path $issPath)) {
    throw "Installer script was not found: $issPath"
}
if (-not (Test-Path $distAppPath)) {
    throw "Packaged SovAuto.exe was not found. Run build_app.ps1 first."
}
foreach ($brandingPath in $installerBranding) {
    if (-not (Test-Path $brandingPath)) {
        throw "Installer branding asset was not found: $brandingPath"
    }
}

$version = (Get-Content $versionFile -Raw).Trim()
if (-not $version) {
    throw "Version file is empty: $versionFile"
}

$installerDir = Join-Path $repoRoot "dist_installer"
$expectedInstaller = Join-Path $installerDir "SovAuto-Setup-$version.exe"
if (Test-Path $expectedInstaller) {
    Remove-Item $expectedInstaller -Force
}

Push-Location $repoRoot
try {
    Write-Host "==> Building SovAuto installer"
    & $isccPath $issPath
    if ($LASTEXITCODE -ne 0) {
        throw "ISCC failed with exit code $LASTEXITCODE"
    }
} finally {
    Pop-Location
}

if (-not (Test-Path $expectedInstaller)) {
    throw "Installer build finished without expected output: $expectedInstaller"
}

Write-Host "==> Installer ready: $expectedInstaller"
