import functools
import inspect
from queue import Queue

from event.event import EventType, Event
from event.observer import Observer
from logger import get_logger
from models.future_tasqq import FutureTasqq
from models.tasqq import Tasqq
from pq.consumeqq import Consumeqq
from utils.data_utils import get_short_id


class Asynqq(Observer):

    def __init__(self, max_workers=0, task_impl=FutureTasqq):
        self.logger = get_logger(__name__)
        self.qq: Queue[Tasqq] = Queue()
        self.consumer_thread = Consumeqq(self.qq, max_workers=max_workers)
        self.task_impl = task_impl
        self.start()

    def start(self):
        self.consumer_thread.start()

    def stop(self):
        self.consumer_thread.stop()
        self.qq.queue.clear()

    def get_qq_size(self):
        return self.qq.qsize()

    def add(self, tqq: Tasqq):
        self.logger.info(f"Adding task {tqq.idx} to queue")
        self.qq.put(tqq)

    def event_update(self, subject, event: Event) -> None:
        if event.e_type in {EventType.START, EventType.STOP}:
            self.logger.info(f"{event.e_type.name} task with id {event.idx}")
        elif event.e_type == EventType.ERROR:
            self.logger.error(f"{event.e_type.name} on task {event.idx}: {event.data}")
        elif event.e_type == EventType.RESULT:
            self.logger.info(f"{event.e_type.name} task {event.idx} completed")

    def task(self, tasqq_id: str = None):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                idx = str(get_short_id() if tasqq_id is None else tasqq_id)
                method = func.__get__(args[0], type(args[0])) if 'self' in inspect.signature(func).parameters else func
                tsk = self.task_impl(idx=idx, func=method, **kwargs)
                tsk.attach(self)
                self.add(tsk)
                return tsk

            async def qq_wrapper(*args, **kwargs):
                w = wrapper(self, *args, **kwargs)
                r = await w.qq(**kwargs)
                return r

            wrapper.qq = qq_wrapper
            return wrapper

        return decorator
