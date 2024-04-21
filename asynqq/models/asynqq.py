import functools
import inspect
from typing import Callable

from asynqq.event.event import EventType, Event
from asynqq.event.observer import Observer
from asynqq.event.subject import Subject
from asynqq.models.future_tasqq import FutureTasqq
from asynqq.models.tasqq import Tasqq
from asynqq.pq.consumeqq import Consumeqq
from asynqq.utils.data_utils import get_short_id
from asynqq.utils.logger import get_logger


class Asynqq(Observer):
    """
    Asynqq class manages tasks in a queue.
    """

    def __init__(self, max_workers=0, task_impl=FutureTasqq, log_level='INFO'):
        """
        Initializes the Asynqq task manager.
        This constructor sets up the task manager with specified parameters and starts the task processing.

        :param max_workers: The maximum number of worker threads. Defaults to 0.
        :param task_impl: The task implementation class. Defaults to FutureTasqq.
        :param log_level: The logging level for the task manager. Defaults to 'INFO'.

        :return: None
        """
        self._logger = get_logger(__name__)
        self._logger.setLevel(log_level)
        self._consumer_thread = Consumeqq(max_workers=max_workers)
        self._task_impl = task_impl
        self._callbacks: dict[str, Subject] = {}
        self.start()

    def start(self):
        """
        Start the consumer thread.
        """
        self._consumer_thread.start()

    def stop(self):
        """
        Stop the consumer thread and clear the queue.
        """
        self._consumer_thread.stop()
        self._consumer_thread.clear_queue()

    def get_qq_size(self):
        """
        Get the size of the queue in the consumer thread.
        """
        return self._consumer_thread.get_queue_size()

    def add(self, func: Callable, idx: str = None, callback: Subject = None, **kwargs) -> Tasqq:
        """
        Adds a task to the task queue.
        This function adds a task to the task queue, optionally associating a callback with it.

        :param func: The function to be executed as a task.
        :param idx: The identifier for the task. Defaults to None.
        :param callback: The callback function associated with the task. Defaults to None.
        :param kwargs: Additional keyword arguments for the task.

        :return Tasqq: The task object that was added to the queue.
        """
        idx = str(get_short_id() if idx is None else idx)
        tqq = self._task_impl(idx=idx, func=func, **kwargs)
        if callback:
            self._callbacks[idx] = callback
        tqq.attach(self)
        self._logger.debug(f"Adding task {tqq.idx} to queue")
        self._consumer_thread.add(tqq)
        return tqq

    def remove(self, idx: str) -> None:
        """
        Removes a task from the task queue.
        This function removes a task from the task queue based on the provided identifier.

        :param idx: The identifier of the task to be removed.

        :return: None
        """
        self._consumer_thread.remove(idx)

    def event_update(self, subject, event: Event) -> None:
        """
        Updates the event handling based on the received event.
        This method processes the event and triggers appropriate actions based on the event type.

        :param subject: The subject associated with the event.
        :param event : The event object to be processed.

        :return: None
        """
        if event.idx in self._callbacks:
            self._callbacks[event.idx].event_notify(event)
        if event.e_type == EventType.START:
            self._logger.debug(f"{event.e_type.name} task with id {event.idx}")
        elif event.e_type == EventType.STOP:
            self._logger.debug(f"{event.e_type.name} task with id {event.idx}")
            if event.idx in self._callbacks:
                del self._callbacks[event.idx]
        elif event.e_type == EventType.ERROR:
            self._logger.error(f"{event.e_type.name} on task {event.idx}: {event.data}")
            if event.idx in self._callbacks:
                del self._callbacks[event.idx]
        elif event.e_type == EventType.RESULT:
            self._logger.debug(f"{event.e_type.name} task {event.idx} completed")
            if event.idx in self._callbacks:
                del self._callbacks[event.idx]

    def task(self, tasqq_id: str = None, callback: Subject = None):
        """
        Decorator for creating and adding tasks to the task queue.
        This function acts as a decorator to create and add tasks to the task queue based on the provided parameters.

        :param tasqq_id: The identifier for the task. Defaults to None.
        :param callback: The callback function associated with the task. Defaults to None.

        :return decorator: The decorator function for creating and adding tasks.
        """

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                idx = str(get_short_id() if tasqq_id is None else tasqq_id)
                method = func.__get__(args[0], type(args[0])) if 'self' in inspect.signature(func).parameters else func
                return self.add(method, idx, callback, **kwargs)

            async def qq_wrapper(*args, **kwargs):
                w = wrapper(self, *args, **kwargs)
                r = await w.qq()
                return r

            wrapper.qq = qq_wrapper
            return wrapper

        return decorator
