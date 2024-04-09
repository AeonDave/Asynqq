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

    def __init__(self, max_workers=0, task_impl=FutureTasqq, log_level='INFO'):
        self._logger = get_logger(__name__)
        self._logger.setLevel(log_level)
        self._consumer_thread = Consumeqq(max_workers=max_workers)
        self._task_impl = task_impl
        self._callbacks: dict[str, Subject] = {}
        self.start()

    def start(self):
        self._consumer_thread.start()

    def stop(self):
        self._consumer_thread.stop()
        self._consumer_thread.clear_queue()

    def get_qq_size(self):
        return self._consumer_thread.get_queue_size()

    def add(self, func: Callable, idx: str = None, callback: Subject = None, **kwargs) -> Tasqq:
        idx = str(get_short_id() if idx is None else idx)
        tqq = self._task_impl(idx=idx, func=func, **kwargs)
        if callback:
            self._callbacks[idx] = callback
        tqq.attach(self)
        self._logger.debug(f"Adding task {tqq.idx} to queue")
        self._consumer_thread.add(tqq)
        return tqq

    def remove(self, idx: str) -> None:
        self._consumer_thread.remove(idx)

    def event_update(self, subject, event: Event) -> None:
        if event.idx in self._callbacks:
            self._callbacks[event.idx].event_notify(event)
        if event.e_type in {EventType.START, EventType.STOP}:
            self._logger.debug(f"{event.e_type.name} task with id {event.idx}")
        elif event.e_type == EventType.ERROR:
            self._logger.error(f"{event.e_type.name} on task {event.idx}: {event.data}")
            if event.idx in self._callbacks:
                del self._callbacks[event.idx]
        elif event.e_type == EventType.RESULT:
            self._logger.debug(f"{event.e_type.name} task {event.idx} completed")
            if event.idx in self._callbacks:
                del self._callbacks[event.idx]

    def task(self, tasqq_id: str = None, callback: Subject = None):
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
