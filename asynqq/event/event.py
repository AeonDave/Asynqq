from enum import Enum


class EventType(Enum):
    """
    EventType is an enumeration that represents the type of events that can occur in the system.
    """
    ERROR = -1  # Represents an error event
    START = 1  # Represents a start event
    STOP = 2  # Represents a stop event
    RESULT = 3  # Represents a result event


class Event:
    """
    Event class represents an event in the system with an id, type, data and optional parameters.
    """

    def __init__(self, idx: str, e_type: EventType, data, **kwargs):
        """
        Initialize an Event with an id, type, data and optional parameters.
        """
        self.idx: str = idx  # The id of the event
        self.e_type: EventType = e_type  # The type of the event
        self.data = data  # The data associated with the event
        self.params: dict = kwargs.get('params', {})  # Optional parameters for the event
