from __future__ import annotations


class RecordingUndoStack:
    def __init__(self) -> None:
        self._items: list[dict] = []

    def push(self, item: dict) -> None:
        self._items.append(item)

    def undo(self) -> dict | None:
        if not self._items:
            return None
        return self._items.pop()

    def items(self) -> list[dict]:
        return list(self._items)

    def clear(self) -> None:
        self._items.clear()
