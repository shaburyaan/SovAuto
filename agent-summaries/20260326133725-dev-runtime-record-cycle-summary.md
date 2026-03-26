# Runtime Record Cycle

- overlay: added Windows-safe non-blocking path with `WindowTransparentForInput` toggle plus native `WS_EX_NOACTIVATE|WS_EX_TRANSPARENT`
- player: wired configurable slow `step_delay` with `4s` default and legacy `300ms` settings normalization
- focus: `activate_window()` now restores, brings to top and requests foreground before per-step playback
- restart: `AppController` now rehydrates existing 1C runtime before record/play after SovAuto restart
- settings: existing `delay_box` now works as slow playback delay source with default `4`
- tests: `pytest tests/test_record_playback_engine.py tests/test_manual_onec_capture.py tests/test_onec_shortcut_service.py` -> `28 passed`
- live: direct `1cv8.exe ENTERPRISE /IBName SOVUT /N ... /P ...` reaches real work window; fresh `python main.py` reaches runtime UI; blocker remains at this agent desktop layer where pywinauto UIA activation of Qt SovAuto buttons does not trigger the real attach slot, so final full gate is still not proven in-session
