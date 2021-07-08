from typing import List, Optional

from requests import Request
from timer import Timer
import numpy as np


class Container:
    def __init__(self, timer: Timer):
        self.queues: List[List[Request]] = [[] for _ in range(5)]
        self.queues_ptr: List[int] = [0 for _ in range(5)]
        self.timer = timer



    def remove_leave(self) -> List[Request]:
        removed = []
        for i in range(5):
            new_queue = []
            for j in range(self.queues_ptr[i], len(self.queues[i])):
                nxt = self.queues[i][j]
                leave_time = nxt.enter_time + nxt.tolerance
                if self.timer.current_time > leave_time:
                    raise Exception()
                if self.timer.current_time == leave_time:
                    removed.append(nxt)
                else:
                    new_queue.append(nxt)
            self.queues[i] = new_queue
            self.queues_ptr[i] = 0
        return removed

    def get_next_leave_time(self) -> int:
        result = np.inf
        for i in range(5):
            for j in range(self.queues_ptr[i], len(self.queues[i])):
                request = self.queues[i][j]
                result = min(result, request.enter_time + request.tolerance)
        return result

    def add_request(self, request: Request) -> None:
        self.queues[request.priority].append(request)

    def next_request(self, pop: bool) -> Optional[Request]:
        for i in range(5):
            if len(self.queues[i]) != self.queues_ptr[i]:
                if pop:
                    self.queues_ptr[i] += 1
                    return self.queues[i][self.queues_ptr[i] - 1]
                else:
                    return self.queues[i][self.queues_ptr[i]]
        return None

    def is_empty(self) -> bool:
        return self.next_request(pop=False) is None
