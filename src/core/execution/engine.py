from __future__ import annotations

import logging
from time import sleep

from core.contracts.event_bus import EventEnvelope, GlobalEventBus
from core.contracts.execution_clock import ExecutionClock
from core.execution.context_snapshot_service import ContextSnapshotService
from core.execution.execution_queue import ExecutionQueue
from core.execution.executor_registry import ExecutorRegistry
from core.execution.pre_step_guard import PreStepGuardPipeline
from core.execution.result_handler import ResultHandler
from core.execution.retry_handler import RetryHandler
from core.execution.run_controller import RunController
from core.execution.state_machine import ExecutionStateMachine
from core.execution.timeout_handler import TimeoutHandler
from core.models.config import Config
from core.models.result import FailureInfo, StepResult
from core.models.state import EngineStatus


class ExecutionEngine:
    def __init__(
        self,
        event_bus: GlobalEventBus,
        logger: logging.Logger,
        registry: ExecutorRegistry,
        guards: PreStepGuardPipeline | None = None,
    ) -> None:
        self.event_bus = event_bus
        self.logger = logger
        self.registry = registry
        self.guards = guards or PreStepGuardPipeline()
        self.clock = ExecutionClock()
        self.timeout_handler = TimeoutHandler(self.clock)
        self.retry_handler = RetryHandler()
        self.snapshot_service = ContextSnapshotService()
        self.state_machine = ExecutionStateMachine()
        self.run_controller: RunController | None = None

    def start(self, config: Config) -> StepResult | None:
        self.run_controller = RunController()
        self.state_machine.transition(EngineStatus.COUNTDOWN)
        self._publish("APP_STATE_CHANGED", {"engine_state": EngineStatus.COUNTDOWN})
        sleep(max(config.settings.countdownSeconds, 0))
        self.state_machine.transition(EngineStatus.RUNNING)
        self._publish("APP_STATE_CHANGED", {"engine_state": EngineStatus.RUNNING})

        execution_queue = ExecutionQueue()
        execution_queue.load(config.steps)
        results = ResultHandler()
        snapshot = self.snapshot_service.build(
            config.metadata.version,
            {"lock_mode": config.settings.lockMode},
        )
        self.logger.info("Execution snapshot prepared: %s", snapshot)

        step = execution_queue.next()
        while step is not None:
            if self.run_controller.cancellation.token.is_cancelled():
                self.state_machine.transition(EngineStatus.STOPPED)
                return StepResult(step_id=step["id"], status="stopped", message="Execution stopped")
            result = self._execute_step(step)
            results.add(result)
            if result.status == "failed":
                self.state_machine.transition(EngineStatus.FAILED)
                return result
            sleep(config.settings.delayBetweenSteps / 1000)
            step = execution_queue.next()

        self.state_machine.transition(EngineStatus.COMPLETED)
        self._publish("APP_STATE_CHANGED", {"engine_state": EngineStatus.COMPLETED})
        return None

    def pause(self) -> None:
        if self.run_controller:
            self.run_controller.request_pause()
            self.state_machine.transition(EngineStatus.PAUSED)
            self._publish("APP_STATE_CHANGED", {"engine_state": EngineStatus.PAUSED})

    def resume(self) -> None:
        if self.run_controller:
            self.run_controller.clear_pause()
            self.state_machine.transition(EngineStatus.RUNNING)
            self._publish("APP_STATE_CHANGED", {"engine_state": EngineStatus.RUNNING})

    def stop(self) -> None:
        if self.run_controller:
            self.run_controller.stop()

    def run_step_debug(self, step: dict) -> StepResult:
        return self._execute_step(step)

    def _execute_step(self, step: dict) -> StepResult:
        started_at = self.clock.now_monotonic()
        self._publish("ENGINE_STEP_EXECUTED", {"step_id": step["id"], "phase": "start"})
        attempts = max(step.get("policy", {}).get("retry", {}).get("count", 1), 1)
        last_error: Exception | None = None
        for attempt in range(1, attempts + 1):
            try:
                self.guards.check(step)
                executor = self.registry.resolve(step["type"])
                executor.execute(step)
                result = StepResult(step_id=step["id"], status="success", message="Step executed")
                self._publish("ENGINE_STEP_EXECUTED", {"step_id": step["id"], "phase": "finish", "status": "success"})
                self.logger.info("Step %s success", step["id"])
                return result
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                self.logger.warning("Step %s attempt %s failed: %s", step["id"], attempt, exc)
                if self.timeout_handler.is_expired(started_at, step.get("timeoutMs", 5000)):
                    break
                if attempt < attempts:
                    self.retry_handler.sleep_interruptible(self.run_controller.cancellation.token, 300)
        self._publish("ENGINE_STEP_EXECUTED", {"step_id": step["id"], "phase": "finish", "status": "failed"})
        return StepResult(
            step_id=step["id"],
            status="failed",
            message=str(last_error) if last_error else "Unknown error",
            failure=FailureInfo(code="ENGINE_ERROR", message=str(last_error) if last_error else "Unknown error"),
        )

    def _publish(self, event_type: str, payload: dict) -> None:
        self.event_bus.publish(
            EventEnvelope(
                event_type=event_type,
                source="execution_engine",
                payload=payload,
                app_state=self.state_machine.state.status,
            )
        )
