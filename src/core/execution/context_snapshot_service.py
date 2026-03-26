from __future__ import annotations

from core.contracts.execution_snapshot import ExecutionContextSnapshot


class ContextSnapshotService:
    def build(self, config_version: str, runtime_flags: dict | None = None) -> ExecutionContextSnapshot:
        return ExecutionContextSnapshot(
            active_config_version=config_version,
            runtime_flags=runtime_flags or {},
            window_state={},
            screen_geometry={},
            input_lock_state=runtime_flags.get("lock_mode", "soft") if runtime_flags else "soft",
        )
