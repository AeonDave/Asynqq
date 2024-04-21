from queue import Queue


class CheckQueue(Queue):
    """
    CheckQueue is a subclass of Python's built-in Queue class.
    It provides additional functionality to check if an item is in the queue and to remove a specific item from the queue.
    """

    def __contains__(self, item) -> bool:
        """
        Check if an item is in the queue.

        Parameters:
        :param item: The item to check for in the queue.

        Returns:
        :return bool: True if the item is in the queue, False otherwise.
        """
        with self.mutex:
            return item in self.queue

    def remove(self, item) -> bool:
        """
        Remove a specific item from the queue.

        Parameters:
        :param  item: The item to remove from the queue.

        Returns:
        :return  bool: True if the item was successfully removed, False otherwise.
        """
        with self.mutex:
            for i in self.queue:
                if i == item:
                    self.queue.remove(i)
                    return True
            return False
