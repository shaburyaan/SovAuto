from __future__ import annotations


class SimulationWindowProvider:
    def get_window(self, process_name: str, title_pattern: str) -> dict:
        return {
            "process_name": process_name,
            "title_pattern": title_pattern,
            "bounds": (100, 100, 1100, 900),
        }
