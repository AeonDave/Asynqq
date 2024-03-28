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

            @asynqq.task(tasqq_id='1')
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
        task4 = asynqq.add(long_duration_function2, idx='4', duration=random.randint(1, 3))
        a, b, c, d = await asyncio.gather(task1, task2, task3, task4.qq())
        print(a)
        print(b)
        print(c)
        print(d)
