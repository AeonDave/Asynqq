import asyncio
import time

from asynqq.event.event import Event, EventType
from asynqq.event.observer import Observer
from asynqq.event.subject import Subject
from asynqq.models.asynqq import Asynqq


class RecordingObserver(Observer):
    def __init__(self):
        self.events: list[Event] = []

    def event_update(self, subject, event: Event) -> None:
        self.events.append(event)


def run(coro):
    return asyncio.run(coro)


def test_instance_method_qq_returns_result_and_notifies_callbacks():
    asynqq = Asynqq(max_workers=1)

    class Callback(Subject):
        def __init__(self):
            super().__init__()
            self.received: list[Event] = []

        def event_update(self, subject, event: Event) -> None:
            self.received.append(event)

    callback = Callback()
    observer = RecordingObserver()
    callback.attach(observer)

    class Worker:
        @asynqq.task(callback=callback)
        def compute(self, value: int, increment: int = 0) -> int:
            return value + increment

    worker = Worker()
    result = run(worker.compute.qq(value=2, increment=3))

    time.sleep(0.05)
    asynqq.stop()

    assert result == 5
    assert observer.events
    assert any(evt.e_type is EventType.RESULT for evt in observer.events)
    assert all(evt.idx == observer.events[0].idx for evt in observer.events)


def test_async_method_runs_inside_executor_event_loop():
    asynqq = Asynqq(max_workers=1)

    class Worker:
        @asynqq.task()
        async def check_loop(self, sleep_for: float = 0.0) -> bool:
            await asyncio.sleep(sleep_for)
            loop = asyncio.get_running_loop()
            return loop.is_running()

    worker = Worker()
    result = run(worker.check_loop.qq(sleep_for=0.01))
    asynqq.stop()

    assert result is True


def test_module_level_function_qq():
    asynqq = Asynqq(max_workers=1)

    @asynqq.task(tasqq_id="fixed")
    def multiply(value: int, factor: int) -> int:
        return value * factor

    result = run(multiply.qq(value=4, factor=3))
    asynqq.stop()

    assert result == 12
