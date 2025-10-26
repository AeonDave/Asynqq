# Asynqq

![pylint](https://img.shields.io/badge/PyLint-8.59-yellow?logo=python&logoColor=white)

Asynqq is a lightweight task queue tailored for local Python applications. It provides a thin abstraction over `asyncio` and `concurrent.futures` to schedule functions, coroutines, or bound methods on a background pool and consume their results through a unified asynchronous interface. The library ships with an event-driven callback system so applications can react to task lifecycle changes without wiring additional infrastructure.

## Key features

- **Local asynchronous execution** – queue synchronous or asynchronous callables and retrieve results through the same `await task.qq()` helper.
- **Descriptor-based decorator** – wrap free functions or instance methods with `@asynqq.task()` without losing binding semantics.
- **Observer callbacks** – plug in `Subject` implementations to receive start, result, stop, and error notifications for each task.
- **Pluggable task backends** – swap out the default `FutureTasqq` implementation if you need custom execution strategies.

## Installation

Install Asynqq into an existing Python 3.9+ environment. From a cloned repository:

```bash
pip install -e .
```

You can also add it to your project dependencies with Poetry:

```bash
poetry add ./
```

## Getting started

Create an `Asynqq` instance with the desired worker count and logging level. Add work to the queue and await completion via the `.qq()` helper exposed on each task.

```python
import asyncio
import datetime
import random
import time

from asynqq.models.asynqq import Asynqq


async def main() -> None:
    asynqq = Asynqq(max_workers=10, log_level="DEBUG")

    def base_func(duration: int) -> str:
        started_at = datetime.datetime.now().isoformat()
        time.sleep(duration)
        return f"Started at {started_at} and ended at {datetime.datetime.now().isoformat()}"

    task = asynqq.add(base_func, duration=random.randint(3, 10)).qq()
    result = await task
    print(result)

    asynqq.stop()


if __name__ == "__main__":
    asyncio.run(main())
```

## Decorating callables

Use `@asynqq.task()` to decorate functions or methods. Decorated callables behave like their original counterparts while exposing an asynchronous `.qq()` helper that schedules work on the queue.

```python
import asyncio
import datetime
import random
import time

from asynqq.models.asynqq import Asynqq


asynqq = Asynqq(max_workers=4)


@asynqq.task()
def blocking(duration: int) -> str:
    time.sleep(duration)
    return f"Completed blocking work in {duration}s"


@asynqq.task()
async def non_blocking(duration: int) -> str:
    await asyncio.sleep(duration)
    return f"Completed async work in {duration}s"


async def main() -> None:
    result = await blocking.qq(duration=random.randint(1, 3))
    print(result)

    other = await non_blocking.qq(duration=2)
    print(other)

    asynqq.stop()


if __name__ == "__main__":
    asyncio.run(main())
```

Decorated instance methods remain bound to their object, so accessing `self` works exactly as expected.

## Working with callbacks

Tasks can publish lifecycle events (`START`, `RESULT`, `STOP`, `ERROR`). Attach a `Subject` when enqueuing work to react to those events. This pattern integrates cleanly with the observer helpers shipped in `asynqq.event`.

```python
import asyncio
import datetime
import time

from asynqq.event.event import Event
from asynqq.event.observer import Observer
from asynqq.event.subject import Subject
from asynqq.models.asynqq import Asynqq


class PrintingCallback(Subject):
    def event_notify(self, event: Event) -> None:
        print(f"[{event.e_type.name}] {event.idx}: {event.data}")
        super().event_notify(event)


class RecordingObserver(Observer):
    def __init__(self) -> None:
        self.events: list[Event] = []

    def event_update(self, subject, event: Event) -> None:
        self.events.append(event)
        print(f"Observer received {event.e_type} for task {event.idx}")


callback = PrintingCallback()
observer = RecordingObserver()
callback.attach(observer)

queue = Asynqq(max_workers=2, log_level="DEBUG")


class Worker:
    @queue.task(callback=callback)
    def long_running(self, duration: int) -> str:
        started_at = datetime.datetime.now().isoformat()
        time.sleep(duration)
        return f"Started at {started_at}"


async def main() -> None:
    worker = Worker()
    result = await worker.long_running.qq(duration=2)
    print(result)
    queue.stop()


if __name__ == "__main__":
    asyncio.run(main())
```

## Running the test suite

Install the development dependencies (via `pip install -r requirements.txt` or `poetry install`) and execute:

```bash
pytest
```

The tests live under the `test/` directory and cover decorators, callback integration, and asynchronous execution semantics.

## License

Distributed under the terms of the MIT License. See the [LICENSE](LICENSE) file for details.
