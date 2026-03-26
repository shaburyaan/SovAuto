from __future__ import annotations

from core.simulation.headless_simulation_engine import HeadlessSimulationEngine


class DeterministicReplayRunner:
    def __init__(self) -> None:
        self.engine = HeadlessSimulationEngine()

    def run_three_times(self, steps: list[dict]) -> bool:
        runs = [self.engine.run(steps) for _ in range(3)]
        return all([result.status for result in runs[0]] == [result.status for result in run] for run in runs[1:])
