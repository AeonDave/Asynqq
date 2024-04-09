import threading
import time
from logging import Logger
from threading import Thread

from asynqq.event.event import Event, EventType
from asynqq.event.observer import Observer
from asynqq.models.tasqq import Tasqq
from asynqq.pq.check_queue import CheckQueue
from asynqq.utils.logger import get_logger


class Consumeqq(Thread, Observer):

    def __init__(self, max_workers=0):
        super(Consumeqq, self).__init__(daemon=True)
        self._logger: Logger = get_logger(__name__)
        self._queue: CheckQueue[Tasqq] = CheckQueue()
        self._max_workers: int = max_workers
        self._stop: bool = False
        self._tasks: dict[str, Tasqq] = {}
        self._queue_lock = threading.Lock()

    def get_queue(self):
        return self._queue

    def clear_queue(self):
        self._queue.queue.clear()

    def get_queue_size(self):
        return self._queue.qsize()

    def get_working_size(self):
        return len(self._tasks)

    def add(self, task: Tasqq):
        with self._queue_lock:
            self._queue.put(task)

    def remove(self, idx):
        with self._queue_lock:
            if idx in self._tasks:
                tqq = self._tasks.pop(idx)
                tqq.stop()
            elif idx in self._queue:
                self._queue.remove(idx)

    def run(self):
        self._logger.debug("Starting Asynqq consumer")
        while not self._stop:
            if 0 < self._max_workers <= self.get_working_size():
                time.sleep(0.2)
                continue
            tqq: Tasqq = self._queue.get()
            if tqq is None:
                continue
            try:
                tqq.attach(self)
                tqq.start()
                self._tasks[tqq.idx] = tqq
            except Exception as ex:
                tqq.add_error(str(ex))
                tqq.event_notify(Event(tqq.idx, EventType.ERROR, f'Error on tasqq start: {ex}'))
        self._logger.debug("Asynqq consumer stopped")
        self._queue.task_done()

    def stop(self):
        self._stop = True
        self.join()

    def event_update(self, subject, event: Event) -> None:
        if event.e_type in [EventType.RESULT, EventType.ERROR] and event.idx in self._tasks:
            self._tasks.pop(event.idx)
