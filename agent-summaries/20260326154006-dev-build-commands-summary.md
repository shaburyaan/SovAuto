# Build Commands

- packaged release now includes `storage/migrations/*.sql`, splash logo path resolves from runtime root, and `dist\SovAuto\tesseract` is bundled from local `C:\Program Files\Tesseract-OCR`
- release scripts are fail-fast: `build_app.ps1` installs build deps, runs PyInstaller, verifies `SovAuto.exe` and bundled OCR; `build_installer.ps1` verifies `ISCC.exe`, packaged app and final installer output
- version flow now syncs `build/version/version.txt`, `pyproject.toml` and `SovAuto.iss`
- PowerShell module `SovAuto.Tools` was added in repo and current-user module paths for Windows PowerShell 5.1 and PowerShell 7; exported commands are `buildAuto` and `pushAutp`
- `buildAuto -Version 1.0.1` succeeded and produced `dist_installer/SovAuto-Setup-1.0.1.exe` plus desktop folder `C:\Users\MLDev\Desktop\SovAuto-Installer-1.0.1`
- smoke install succeeded to `C:\Users\MLDev\AppData\Local\Temp\SovAutoSmokeInstall`, bundled `tesseract.exe` exists there, and launched installed `SovAuto.exe`
