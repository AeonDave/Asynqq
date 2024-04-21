from abc import ABC
from typing import List

from asynqq.event.event import Event


class Subject(ABC):
    """
    Subject is an abstract base class that represents a subject in the observer design pattern.
    A subject is an object that has one or more observers that are interested in its state.
    The subject maintains a list of its observers and notifies them of any state changes.

    The observer pattern is a software design pattern in which an object, called the subject,
    maintains a list of its dependents, called observers, and notifies them automatically of any state changes,
    usually by calling one of their methods.
    """

    def __init__(self):
        """
        Initialize a Subject with a list of observers.
        """
        self._observers: List = []

    def attach(self, observer) -> None:
        """
        Attach an observer to the subject.

        Parameters:
        observer: The observer to be attached.
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer) -> None:
        """
        Detach an observer from the subject.

        Parameters:
        observer: The observer to be detached.
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def detach_all(self) -> None:
        """
        Detach all observers from the subject.
        """
        self._observers.clear()

    def event_notify(self, event: Event) -> None:
        """
        Notify all attached observers of an event.

        Parameters:
        event (Event): The event that the observers should be notified about.
        """
        for observer in self._observers:
            observer.event_update(self, event)
