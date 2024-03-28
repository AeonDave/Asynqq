from abc import ABC
from typing import List

from event.event import Event


class Subject(ABC):
    def __init__(self):
        self._observers: List = []

    def attach(self, observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def detach_all(self) -> None:
        self._observers.clear()

    def event_notify(self, event: Event) -> None:
        for observer in self._observers:
            observer.event_update(self, event)
