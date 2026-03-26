# SovAuto product finish summary

- added 1C launcher/profile memory layer with autodiscovery + settings persistence
- rebuilt main shell: left nav, center 1C host, bottom action bar, right status/log pane
- added splash spinner/loading text, onboarding overlay, toast feedback, centralized Russian strings
- added UI telemetry + 1C session events + profile tests
- verified: compileall, pytest 6 passed, source smoke, packaged exe smoke, installer rebuild
- blocked: real 1C attach flow not validated on this machine because `1cv8.exe` is absent
