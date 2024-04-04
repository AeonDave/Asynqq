from logging import Logger
from queue import Queue
from threading import Thread

from asynqq.event.event import Event, EventType
from asynqq.utils.logger import get_logger
from asynqq.models.tasqq import Tasqq


class Consumeqq(Thread):
    def __init__(self, queue: Queue[Tasqq], max_workers=0):
        super(Consumeqq, self).__init__(daemon=True)
        self.logger: Logger = get_logger(__name__)
        self.queue: Queue[Tasqq] = queue
        self.max_workers: int = max_workers
        self._stop: bool = False

    def run(self):
        self.logger.info("Starting Asynqq consumer")
        while not self._stop:
            if self.max_workers > 0:
                if self.queue.qsize() >= self.max_workers:
                    continue
            tqq: Tasqq = self.queue.get()
            if tqq is None:
                continue
            try:
                tqq.start()
            except Exception as ex:
                tqq.add_error(str(ex))
                tqq.event_notify(Event(tqq.idx, EventType.ERROR, f'Error on tasqq start: {ex}'))
        self.logger.info("Asynqq consumer stopped")
        self.queue.task_done()

    def stop(self):
        self._stop = True
        self.join()
