import asyncio
import time

import pytest

from asynqq.event.event import Event, EventType
from asynqq.event.observer import Observer
from asynqq.event.subject import Subject
from asynqq.models.asynqq import Asynqq


def run(coro):
    return asyncio.run(coro)


class RecordingObserver(Observer):
    def __init__(self):
        self.events: list[Event] = []

    def event_update(self, subject, event: Event) -> None:
        self.events.append(event)


class RecordingCallback(Subject):
    def __init__(self):
        super().__init__()
        self.forwarded: list[Event] = []

    def event_notify(self, event: Event) -> None:
        self.forwarded.append(event)
        super().event_notify(event)


@pytest.fixture()
def task_manager():
    manager = Asynqq(max_workers=2)
    yield manager
    manager._consumer_thread.add(None)
    manager.stop()


def test_add_runs_sync_function_and_notifies_callback(task_manager):
    callback = RecordingCallback()
    observer = RecordingObserver()
    callback.attach(observer)

    def compute(value: int, increment: int = 0) -> int:
        return value + increment

    task = task_manager.add(compute, idx="sync", callback=callback, value=2, increment=3)
    result = run(task.qq())

    assert result == 5
    assert any(evt.e_type is EventType.RESULT for evt in observer.events)
    assert all(evt.idx == "sync" for evt in observer.events)
    assert any(evt.e_type is EventType.RESULT for evt in callback.forwarded)


def test_decorated_instance_method_returns_task_and_result(task_manager):
    callback = RecordingCallback()
    observer = RecordingObserver()
    callback.attach(observer)

    class Worker:
        @task_manager.task(callback=callback)
        def compute(self, value: int, increment: int = 1) -> int:
            return value + increment

    worker = Worker()

    task = worker.compute(value=4, increment=2)
    assert hasattr(task, "qq")

    result = run(worker.compute.qq(value=4, increment=2))

    assert result == 6
    assert any(evt.e_type is EventType.RESULT for evt in observer.events)


def test_decorated_async_method_waits_for_coroutine(task_manager):
    class Worker:
        @task_manager.task()
        async def check_loop(self, sleep_for: float = 0.0) -> bool:
            await asyncio.sleep(sleep_for)
            loop = asyncio.get_running_loop()
            return loop.is_running()

    worker = Worker()
    result = run(worker.check_loop.qq(sleep_for=0.01))

    assert result is True


def test_module_level_task_decorator(task_manager):
    @task_manager.task(tasqq_id="fixed")
    def multiply(value: int, factor: int) -> int:
        return value * factor

    result = run(multiply.qq(value=4, factor=3))

    assert result == 12


def test_add_accepts_coroutine_function(task_manager):
    async def compute(delay: float, value: int) -> int:
        await asyncio.sleep(delay)
        return value

    task = task_manager.add(compute, idx="async", delay=0.01, value=42)
    result = run(task.qq())

    assert result == 42


def test_failing_task_notifies_error(task_manager):
    callback = RecordingCallback()
    observer = RecordingObserver()
    callback.attach(observer)

    def boom() -> None:
        raise RuntimeError("explosion")

    task = task_manager.add(boom, idx="fail", callback=callback)
    result = run(task.qq())

    error_events = [evt for evt in observer.events if evt.e_type is EventType.ERROR]
    assert result == []
    assert error_events
    assert any("explosion" in message for message in error_events[-1].data)
    assert any(evt.e_type is EventType.ERROR for evt in callback.forwarded)


def test_multiple_tasks_drain_queue(task_manager):
    def sleeper_factory(label: str):
        def do_sleep(duration: float) -> str:
            time.sleep(duration)
            return label

        return do_sleep

    first = task_manager.add(sleeper_factory("t1"), idx="t1", duration=0.02)
    second = task_manager.add(sleeper_factory("t2"), idx="t2", duration=0.01)

    async def wait_all():
        return await asyncio.gather(first.qq(), second.qq())

    results = run(wait_all())

    assert set(results) == {"t1", "t2"}
    assert task_manager.get_qq_size() == 0
