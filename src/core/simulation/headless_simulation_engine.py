from __future__ import annotations

from core.models.result import StepResult
from core.simulation.simulation_screen_provider import SimulationScreenProvider
from core.simulation.simulation_window_provider import SimulationWindowProvider


class HeadlessSimulationEngine:
    def __init__(self) -> None:
        self.screen = SimulationScreenProvider()
        self.window = SimulationWindowProvider()

    def run(self, steps: list[dict]) -> list[StepResult]:
        results: list[StepResult] = []
        for step in steps:
            results.append(StepResult(step_id=step["id"], status="success", message="Simulated"))
        return results
