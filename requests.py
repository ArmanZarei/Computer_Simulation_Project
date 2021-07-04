from dataclasses import dataclass
import numpy as np
import settings
import random


def random_tolerance() -> int:
    return int(random.expovariate(1 / settings.alpha))


def random_interval_lambda() -> int:
    return int(random.expovariate(settings.interval_lambda))


def random_priority() -> int:
    x = random.random()
    if x < 0.5:
        return 0
    if x < 0.7:
        return 1
    if x < 0.85:
        return 2
    if x < 0.95:
        return 3
    return 4


@dataclass
class Request:
    GlobalTime = 0

    enter_time: int
    priority: int
    tolerance: int

    @staticmethod
    def gen() -> 'Request':
        Request.GlobalTime += random_interval_lambda()
        return Request(
            enter_time=Request.GlobalTime,
            priority=random_priority(),
            tolerance=random_tolerance(),
        )

    def __gt__(self, r2: 'Request'):
        if self.priority > r2.priority:
            return True
        elif self.priority == r2.priority and self.enter_time < r2.enter_time:
            return True
        return False

    def __str__(self):
        return "Time: %d, Priorty: %d, Tolerance: %d" % (self.enter_time, self.priority, self.tolerance)

class RequestHeap:
    def __init__(self, size):
        self.heap = [Request(-1, np.inf, 0)]
        self.ptr = 1

    def swap(self, ptr1, ptr2):
        self.heap[ptr1], self.heap[ptr2] = self.heap[ptr2], self.heap[ptr1]

    def bubble_up(self):
        ptr = self.ptr - 1
        while self.heap[ptr] > self.heap[ptr // 2]:
            self.swap(ptr, ptr // 2)
            ptr = ptr // 2

    def bubble_down(self):
        ptr = 1
        while True:
            if 2 * ptr + 1 < self.ptr and self.heap[ptr] < self.heap[ptr * 2 + 1]:
                tmp_ptr = 2 * ptr + 1
                if self.heap[ptr * 2] > self.heap[ptr * 2 + 1]:
                    tmp_ptr = ptr * 2
                self.swap(ptr, tmp_ptr)
                ptr = tmp_ptr
            elif 2 * ptr < self.ptr and self.heap[ptr] < self.heap[ptr * 2]:
                self.swap(ptr, ptr * 2)
                ptr *= 2
            else:
                break

    def add(self, req: Request):
        self.heap[self.ptr] = req
        self.ptr += 1
        self.bubble_up()

    def top(self):
        if self.ptr > 1:
            return self.heap[1]
        return None
    
    def pop(self):
        top = self.top()
        self.ptr -= 1
        self.heap[1] = self.heap[self.ptr]
        self.bubble_down()

        return top
    
    def is_empty(self):
        return self.ptr == 1

test_requests = [Request.gen() for _ in range(50)]
req_heap = RequestHeap(len(test_requests))
for req in test_requests:
    req_heap.add(req)

for _ in range(len(test_requests)):
    print(req_heap.pop())
