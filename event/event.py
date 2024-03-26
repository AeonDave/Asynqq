from enum import Enum


class EventType(Enum):
    ERROR = -1
    START = 1
    STOP = 2
    RESULT = 3


class Event:
    def __init__(self, idx: str, e_type: EventType, data, **kwargs):
        self.idx: str = idx
        self.e_type: EventType = e_type
        self.data = data
        self.params: dict = kwargs.get('params', {})
