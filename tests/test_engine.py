import logging

from core.contracts.event_bus import GlobalEventBus
from core.execution.engine import ExecutionEngine
from core.execution.executor_registry import ExecutorRegistry
from core.models.config import Config


class DummyExecutor:
    def __init__(self) -> None:
        self.executed = 0

    def execute(self, step: dict) -> None:
        self.executed += 1


def test_engine_executes_steps() -> None:
    registry = ExecutorRegistry()
    dummy = DummyExecutor()
    registry.register("click", dummy)
    engine = ExecutionEngine(GlobalEventBus(), logging.getLogger("test"), registry)
    config = Config(
        name="Engine Test",
        steps=[
            {"id": "1", "type": "click"},
            {"id": "2", "type": "click"},
        ],
    )
    config.settings.countdownSeconds = 0
    result = engine.start(config)
    assert result is None
    assert dummy.executed == 2
