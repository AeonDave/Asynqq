from abc import abstractmethod, ABC

from asynqq.event.event import Event


class Observer(ABC):
    """
    Observer is an abstract base class that represents an observer in the observer design pattern.
    An observer is an object that wishes to be informed about events happening in the system.
    The observer pattern is a software design pattern in which an object, called the subject,
    maintains a list of its dependents, called observers, and notifies them automatically of any state changes,
    usually by calling one of their methods.
    """

    @abstractmethod
    def event_update(self, subject, event: Event) -> None:
        """
        Abstract method that is called to update the observer about an event.
        This method should be implemented by any concrete class that inherits from this abstract base class.

        Parameters:
        subject: The subject that the observer is observing.
        event (Event): The event that the observer is being updated about.
        """
        pass
