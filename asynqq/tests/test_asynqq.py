import asyncio
import datetime
import random
import time
import unittest

from asynqq.event.event import Event
from asynqq.event.observer import Observer
from asynqq.event.subject import Subject
from asynqq.models.asynqq import Asynqq


class Callback(Subject):
    def __init__(self, idx: str):
        super().__init__()
        self.idx = idx


class TestAsynqq(Observer, unittest.IsolatedAsyncioTestCase):

    def event_update(self, subject, event: Event) -> None:
        print('event')

    async def test_asynqq_base_test(self):
        asynqq = Asynqq(max_workers=10, log_level='DEBUG')

        def base_func(duration):
            dd = datetime.datetime.now().isoformat()
            time.sleep(duration)
            return f'Started at {dd} and ended at {datetime.datetime.now().isoformat()}'

        task = asynqq.add(base_func, duration=random.randint(3, 10)).qq()

        print(await task)

    async def test_asynqq_base_decorator_test(self):
        asynqq = Asynqq(max_workers=10, log_level='DEBUG')

        @asynqq.task()
        def base_func(duration):
            dd = datetime.datetime.now().isoformat()
            time.sleep(duration)
            return f'Started at {dd} and ended at {datetime.datetime.now().isoformat()}'

        task = base_func.qq(duration=random.randint(3, 10))
        print(await task)


    async def test_asynqq_all_tasks_complete(self):
        asynqq = Asynqq(max_workers=10, log_level='DEBUG')

        callback = Callback('1')
        callback.attach(self)

        class Work:

            @asynqq.task(tasqq_id='1', callback=callback)
            def long_class_duration_function(self, duration):
                dd = datetime.datetime.now().isoformat()
                time.sleep(duration)
                return f'Started at {dd} and ended at {datetime.datetime.now().isoformat()}'

            @asynqq.task(tasqq_id='2')
            async def long_class_duration_function_async(self, duration):
                dd = datetime.datetime.now().isoformat()
                await asyncio.sleep(duration)
                return f'Started at {dd} and ended at {datetime.datetime.now().isoformat()}'

        @asynqq.task(tasqq_id='3')
        def long_duration_function(duration):
            dd = datetime.datetime.now().isoformat()
            time.sleep(duration)
            return f'Started at {dd} and ended at {datetime.datetime.now().isoformat()}'

        def long_duration_function2(duration):
            dd = datetime.datetime.now().isoformat()
            time.sleep(duration)
            return f'Started at {dd} and ended at {datetime.datetime.now().isoformat()}'

        work_instance = Work()
        task1 = work_instance.long_class_duration_function.qq(duration=random.randint(1, 3))
        task2 = work_instance.long_class_duration_function_async.qq(duration=random.randint(1, 3))
        task3 = long_duration_function.qq(duration=random.randint(1, 3))
        task4 = asynqq.add(long_duration_function2, duration=random.randint(1, 3))
        a, b, c, d = await asyncio.gather(task1, task2, task3, task4.qq())
        print(a)
        print(b)
        print(c)
        print(d)
