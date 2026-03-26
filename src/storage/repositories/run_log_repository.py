from __future__ import annotations

import json

from storage.db import DatabaseProvider


class RunLogRepository:
    def __init__(self, provider: DatabaseProvider) -> None:
        self.provider = provider

    def append(self, run_id: str, step_id: str, status: str, payload: dict) -> None:
        with self.provider.connect() as connection:
            connection.execute(
                """
                INSERT INTO run_logs (run_id, step_id, status, payload)
                VALUES (?, ?, ?, ?)
                """,
                (run_id, step_id, status, json.dumps(payload, ensure_ascii=False)),
            )
            connection.commit()
