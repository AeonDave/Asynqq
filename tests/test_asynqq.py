import asyncio
import datetime
import random
import time
import unittest

from asynqq import Asynqq


class TestAsynqq(unittest.IsolatedAsyncioTestCase):

    async def test_asynqq_all_tasks_complete(self):
        asynqq = Asynqq(max_workers=10)

        class Work:

            @asynqq.task()
            def long_class_duration_function(self, duration):
                d = datetime.datetime.now().isoformat()
                time.sleep(duration)
                return f'Started at {d} and ended at {datetime.datetime.now().isoformat()}'

            @asynqq.task()
            async def long_class_duration_function_async(self, duration):
                d = datetime.datetime.now().isoformat()
                await asyncio.sleep(duration)
                return f'Started at {d} and ended at {datetime.datetime.now().isoformat()}'

        @asynqq.task(tasqq_id='1234')
        def long_duration_function(duration):
            d = datetime.datetime.now().isoformat()
            time.sleep(duration)
            return f'Started at {d} and ended at {datetime.datetime.now().isoformat()}'

        work_instance = Work()
        task1 = work_instance.long_class_duration_function.qq(duration=random.randint(1, 3))
        task2 = work_instance.long_class_duration_function_async.qq(duration=random.randint(1, 3))
        task3 = long_duration_function.qq(duration=random.randint(1, 3))
        a, b, c = await asyncio.gather(task1, task2, task3)
        print(a)
        print(b)
        print(c)
