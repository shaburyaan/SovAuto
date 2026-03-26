from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from core.models.config import Config
from storage.repositories.config_repository import ConfigRepository


def _now() -> str:
    return datetime.now(UTC).isoformat()


class ScenarioManager:
    def __init__(self, repository: ConfigRepository) -> None:
        self.repository = repository

    def list_scenarios(self) -> list[Config]:
        return [config for config in self.repository.get_all() if self._is_scenario(config)]

    def save_scenario(self, name: str, steps: list[dict[str, Any]], config_id: str | None = None) -> Config:
        name = name.strip()
        if not name:
            raise ValueError("Имя сценария обязательно")
        existing = self.repository.get(config_id) if config_id else None
        scenario = existing or Config(name=name)
        scenario.name = name
        scenario.steps = list(steps)
        scenario.metadata.updatedAt = _now()
        self.repository.save(scenario)
        return scenario

    def load_scenario(self, config_id: str) -> Config | None:
        return self.repository.get(config_id)

    def delete_scenario(self, config_id: str) -> None:
        self.repository.delete(config_id)

    def _is_scenario(self, config: Config) -> bool:
        if not config.steps:
            return False
        for step in config.steps:
            if step.get("type") not in {"click", "input"}:
                return False
            if "x" not in step or "y" not in step:
                return False
        return True
