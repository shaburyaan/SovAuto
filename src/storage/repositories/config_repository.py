from __future__ import annotations

import json
from pathlib import Path

from core.models.config import Config
from storage.db import DatabaseProvider
from storage.serializers.config_serializer import ConfigSerializer


class ConfigRepository:
    def __init__(self, provider: DatabaseProvider, configs_dir: Path) -> None:
        self.provider = provider
        self.configs_dir = configs_dir
        self.serializer = ConfigSerializer()

    def save(self, config: Config) -> None:
        payload = json.dumps(config.to_dict(), ensure_ascii=False)
        with self.provider.connect() as connection:
            connection.execute(
                """
                INSERT INTO configs (id, name, version, created_at, updated_at, payload)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                  name = excluded.name,
                  version = excluded.version,
                  updated_at = excluded.updated_at,
                  payload = excluded.payload
                """,
                (
                    config.id,
                    config.name,
                    config.metadata.version,
                    config.metadata.createdAt,
                    config.metadata.updatedAt,
                    payload,
                ),
            )
            connection.commit()
        self.serializer.dump(config, self.configs_dir / f"{config.name}.json")

    def get_all(self) -> list[Config]:
        with self.provider.connect() as connection:
            rows = connection.execute("SELECT payload FROM configs ORDER BY updated_at DESC").fetchall()
        return [self.serializer.from_dict(json.loads(row["payload"])) for row in rows]

    def get(self, config_id: str) -> Config | None:
        with self.provider.connect() as connection:
            row = connection.execute(
                "SELECT payload FROM configs WHERE id = ?",
                (config_id,),
            ).fetchone()
        if row is None:
            return None
        return self.serializer.from_dict(json.loads(row["payload"]))

    def delete(self, config_id: str) -> None:
        with self.provider.connect() as connection:
            connection.execute("DELETE FROM configs WHERE id = ?", (config_id,))
            connection.commit()
