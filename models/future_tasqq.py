import asyncio
from asyncio import Future
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Optional

from event.event import EventType, Event
from models.tasqq import Tasqq

# Create a ThreadPoolExecutor instance
executor = ThreadPoolExecutor()


class FutureTasqq(Tasqq):
    """
    FutureTasqq is a subclass of Tasqq that represents a task that will be executed in the future.
    It uses a ThreadPoolExecutor to run the task in a separate thread.
    """

    def __init__(self, idx, func, **kwargs):
        """
        Initialize a FutureTasqq instance.

        :param idx: The unique identifier for the task.
        :param func: The function to be executed by the task.
        :param kwargs: Additional keyword arguments.
        """
        super().__init__(idx, **kwargs)
        self.executor: ThreadPoolExecutor = executor
        self.func: Callable = func
        self.future_executor: Optional[Future] = None
        self.completed = False

    def is_running(self) -> bool:
        """
        Check if the task is running.

        :return: True if the task is running, False otherwise.
        """
        return self.future_executor is not None and not self.future_executor.done()

    def is_completed(self) -> bool:
        """
        Check if the task has completed.

        :return: True if the task has completed, False otherwise.
        """
        return self.completed

    def start(self):
        """
        Start the task by submitting it to the executor.
        Also, notify the start event.
        """
        self.future_executor = self.executor.submit(self.run)
        self.event_notify(
            Event(
                self.idx,
                EventType.START,
                None,
                **self.kwargs
            )
        )

    def stop(self):
        """
        Stop the task if it is running.
        Also, notify the stop event.
        """
        if self.future_executor and not self.future_executor.done():
            self.future_executor.cancel()
        del self.future_executor
        self.completed = True
        self.event_notify(
            Event(
                self.idx,
                EventType.STOP,
                None,
                **self.kwargs
            )
        )

    def get_result(self) -> object:
        """
        Get the result of the task.

        :return: The result of the task.
        """
        return self.result

    async def qq(self):
        while not self.completed:
            await asyncio.sleep(0.1)
        return self.result

    def run(self):
        """
        Run the task and set the result.
        If the task function is a coroutine, it is run in an asyncio event loop.
        If the task encounters an exception, it is added to the errors and the error event is notified.
        After the task is run, the result event is notified.
        """
        try:
            if asyncio.iscoroutinefunction(self.func):
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_closed():
                        raise RuntimeError('loop is closed')
                except RuntimeError as ex:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                try:
                    self.result = loop.run_until_complete(self.func(**self.kwargs))
                finally:
                    loop.close()
            else:
                self.result = self.func(**self.kwargs)
            self.event_notify(
                Event(
                    self.idx,
                    EventType.RESULT,
                    self.result,
                    **self.kwargs
                )
            )
        except Exception as ex:
            self.errors.append(str(ex))
            self.event_notify(
                Event(
                    self.idx,
                    EventType.ERROR,
                    ex,
                    **self.kwargs
                )
            )
        finally:
            self.completed = True
            self.detach_all()
