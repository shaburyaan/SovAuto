from __future__ import annotations

import json

from storage.db import DatabaseProvider


class SettingsRepository:
    def __init__(self, provider: DatabaseProvider) -> None:
        self.provider = provider

    def set(self, key: str, value: dict) -> None:
        with self.provider.connect() as connection:
            connection.execute(
                """
                INSERT INTO app_settings (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (key, json.dumps(value, ensure_ascii=False)),
            )
            connection.commit()

    def get(self, key: str, default: dict | None = None) -> dict:
        with self.provider.connect() as connection:
            row = connection.execute(
                "SELECT value FROM app_settings WHERE key = ?",
                (key,),
            ).fetchone()
        if row is None:
            return default or {}
        return json.loads(row["value"])
