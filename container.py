from typing import List, Optional

from requests import Request
from timer import Timer


class Container:
    """
    This class is implementation of system's queue

    Attributes:
        left: list of customers who left the system
    """

    def __init__(self, timer: Timer):
        self.queues: List[List[Request]] = [[] for _ in range(5)]
        self.queues_ptr: List[int] = [0 for _ in range(5)]
        self.timer = timer
        self.left: List[Request] = []

    def add_request(self, request: Request) -> None:
        self.queues[request.priority].append(request)

    def next_request(self, pop: bool) -> Optional[Request]:
        for i in range(4, -1, -1):
            while self.queues_ptr[i] < len(self.queues[i]):
                if (
                    self.queues[i][self.queues_ptr[i]].leave_time()
                    <= self.timer.current_time
                ):
                    self.left.append(self.queues[i][self.queues_ptr[i]])
                    self.queues_ptr[i] += 1
                    continue
                if pop:
                    self.queues_ptr[i] += 1
                    return self.queues[i][self.queues_ptr[i] - 1]
                else:
                    return self.queues[i][self.queues_ptr[i]]
        return None

    def is_empty(self) -> bool:
        return self.next_request(pop=False) is None
