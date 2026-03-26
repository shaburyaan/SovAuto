Playback focus fixes code landed.

- overlay now no-focus/no-activate; playback has separate countdown/playback/completion rendering
- scenario save now strips name and rejects empty input
- playback now returns to home area, activates 1C before countdown and before each step, validates hwnd/rect/bounds, shows explicit click indicator
- pytest passed: 25/25 (`test_record_playback_engine`, `test_manual_onec_capture`, `test_onec_shortcut_service`)
- live runtime advanced through real 1C launcher -> login -> working window, but detached SovAuto still did not switch from manual-capture state after `Захватить 1С`, so final embedded record/playback gate is still open
