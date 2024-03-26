import datetime
from abc import abstractmethod, ABC

from event.event import Event, EventType
from event.subject import Subject


class Tasqq(Subject, ABC):
    """
    Tasqq is an abstract base class that represents a task. It inherits from the Subject class
    and the ABC (Abstract Base Class) class. It provides the basic structure and methods for a task.
    """

    def __init__(self, idx, **kwargs):
        """
        Initialize a Tasqq instance.

        :param idx: The unique identifier for the task.
        :param kwargs: Additional keyword arguments.
        """
        super().__init__()
        self.kwargs: dict = kwargs
        self.idx: str = idx
        self.errors: list[str] = []
        self.result: object = []
        self.created_at: datetime = datetime.datetime.now(datetime.timezone.utc)
        self.completed: bool = False

    def __eq__(self, o: object) -> bool:
        """
        Check if the task is equal to another object.

        :param o: The object to compare with.
        :return: True if the task is equal to the object, False otherwise.
        """
        if isinstance(o, self.__class__):
            return self.idx == o.idx
        elif isinstance(o, str):
            return self.idx == o
        else:
            return False

    def __hash__(self):
        """
        Get the hash value of the task.

        :return: The hash value of the task.
        """
        return hash(self.idx)

    def __str__(self):
        """
        Get the string representation of the task.

        :return: The string representation of the task.
        """
        return f"idx={self.idx} created_at={self.created_at}"

    @abstractmethod
    def is_running(self) -> bool:
        """
        Check if the task is currently running.

        :return: True if the task is running, False otherwise.
        """
        pass

    @abstractmethod
    def is_completed(self) -> bool:
        """
        Check if the task has completed.

        :return: True if the task has completed, False otherwise.
        """
        pass

    @abstractmethod
    def start(self):
        """
        Start the task. This method should be implemented by subclasses.
        """
        pass

    @abstractmethod
    def stop(self):
        """
        Stop the task. This method should be implemented by subclasses.
        """
        pass

    @abstractmethod
    def get_result(self) -> object:
        """
        Return the result of the task.

        :return: The result of the task.
        """
        pass

    @abstractmethod
    async def qq(self, **kwargs) -> object:
        """
        Await the result of the task while pending.

        :return: The result of the task.
        """
        pass

    def add_error(self, err: str):
        """
        Add an error to the task.

        :param err: The error to add.
        """
        self.errors.append(err)

    def push_result(self, result: object, is_error: bool):
        """
        Push a result to the task and notify the event.

        :param result: The result to push.
        :param is_error: Whether the result is an error.
        """
        self.result = result
        self.event_notify(
            Event(
                self.idx,
                EventType.ERROR if is_error else EventType.RESULT,
                self.result,
                **self.kwargs
            )
        )
