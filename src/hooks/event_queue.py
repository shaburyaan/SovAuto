from __future__ import annotations

from queue import Queue

from core.contracts.normalized_events import RawInputEvent


class HookEventQueue:
    def __init__(self) -> None:
        self.queue: Queue[RawInputEvent] = Queue()

    def put(self, event: RawInputEvent) -> None:
        self.queue.put(event)

    def get(self) -> RawInputEvent:
        return self.queue.get()
