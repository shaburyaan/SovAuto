# Branding And Push

- branded assets were generated under `build/branding`: `sovauto.ico`, `wizard-image.bmp`, `wizard-small.bmp`, `sovauto-logo.png`
- packaged/runtime branding now uses `sovauto-logo.png` and `sovauto.ico`; packaged fallback checks both app root and `_internal`
- `SovAuto.iss` and `sovauto.spec` now apply installer/app branding; build scripts fail fast if branding assets are missing
- current-user PowerShell 5.1 and 7 modules now export `pushAuto`; old `pushAutp` no longer resolves
- README and package/module descriptions were expanded to bilingual RU/EN product descriptions
- `buildAuto -Version 1.0.3` succeeded; silent install to `C:\Users\MLDev\Desktop\SovAutoSmokeInstall` succeeded; installed `SovAuto.exe` stayed alive and installed `_internal` contains branded logo
- first real publish found bootstrap `README.md` add/add conflict and interactive HTTPS push hang; `pushAuto` was hardened to auto-resolve bootstrap README conflict in favor of local README and push via `gh auth token` URL without git config changes
