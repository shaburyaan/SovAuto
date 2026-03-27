# PushAuto Fix

- `pushAuto` was simplified to the same push model as `pushSov`: `git add -A` -> `git commit` -> detect current branch -> `git push -u origin <branch>`
- hard dependency on `gh auth token` and token URL push was removed
- GitHub description update is still attempted, but now only as a non-blocking post-step with warning output
- Windows PowerShell 5.1 and PowerShell 7 module copies were updated too
- module import works in both shells and `git push --dry-run origin main` now succeeds for SovAuto
