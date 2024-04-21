# Asynqq
Asynqq is a Python library for managing a local queue of asynchronous tasks.
It allows you to create tasks of your own functions and executed in parallel and asynchronously, all local without external workers.
This enables an efficient usage of computational resources, facilitating simultaneous operations and thereby improving development agility and time optimization.

## Features

- Asynchronous task management: Asynqq uses Python's asyncio library to manage tasks asynchronously.
- Task queue: Tasks are managed in a queue, allowing for efficient task management.
- Customizable: Asynqq allows for customization of task implementation and logging level.

## Implemented tasks

- Future tasks: Run task with future ThreadPoolExecutor()

## Usage

#### Basic
```python
asynqq = Asynqq(max_workers=10, log_level='DEBUG')

def base_func(duration):
    dd = datetime.datetime.now().isoformat()
    time.sleep(duration)
    return f'Started at {dd} and ended at {datetime.datetime.now().isoformat()}'

task = asynqq.add(base_func, duration=random.randint(3, 10)).qq()

print(await task)

```

#### With decorator
```python
asynqq = Asynqq(max_workers=10, log_level='DEBUG')

@asynqq.task()
def base_func(duration):
    dd = datetime.datetime.now().isoformat()
    time.sleep(duration)
    return f'Started at {dd} and ended at {datetime.datetime.now().isoformat()}'

task = base_func.qq(duration=random.randint(3, 10))
print(await task)

```

#### With class and callbacks
You can use the Observer pattern to implement callbacks in your tasks.
Functions can be asynchronous or synchronous.
```python

class MyCallback(Subject):
    def __init__(self, idx: str):
        super().__init__()
        self.idx = idx
        
class MyClass(Observer):
    
    # Implementing the Observer event_update method
    def event_update(self, subject, event: Event) -> None:
        print('event')
        
    asynqq = Asynqq(max_workers=10, log_level='DEBUG')
    
    class Work:
        
        # Adding function with custom id and callback
        @asynqq.task(tasqq_id='1', callback=callback)
        def base_func(self, duration):
            dd = datetime.datetime.now().isoformat()
            time.sleep(duration)
            return f'Started at {dd} and ended at {datetime.datetime.now().isoformat()}'
    
        @asynqq.task(tasqq_id='2')
        async def async_base_func(self, duration):
            dd = datetime.datetime.now().isoformat()
            await asyncio.sleep(duration)
            return f'Started at {dd} and ended at {datetime.datetime.now().isoformat()}'

    work_instance = Work()
    task1 = work_instance.base_func.qq(duration=random.randint(3, 10))
    task2 = work_instance.async_base_func.qq(duration=random.randint(3, 10))
    t1, t2 = await asyncio.gather(task1, task2)
    print(t1, t2)

```