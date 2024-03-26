from abc import abstractmethod, ABC

from event.event import Event


class Observer(ABC):

    @abstractmethod
    def event_update(self, subject, event: Event) -> None:
        pass
