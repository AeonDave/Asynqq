from queue import Queue


class CheckQueue(Queue):
    def __contains__(self, item):
        with self.mutex:
            return item in self.queue

    def remove(self, item):
        with self.mutex:
            for i in self.queue:
                if i == item:
                    self.queue.remove(i)
                    return True
            return False
