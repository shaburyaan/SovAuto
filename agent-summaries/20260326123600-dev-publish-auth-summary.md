# Publish Auth

- real `git push` to `shaburyaan/SovAuto` was attempted and GitHub returned `403`
- `gh repo view shaburyaan/SovAuto --json viewerPermission` reports `READ` for the active account, so remote push/about update cannot complete from the current auth context
- `pushAuto` was hardened again: it now checks `viewerPermission` before `git add/commit`, so future runs fail fast with a clear write-access error instead of creating extra commits
