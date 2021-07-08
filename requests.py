from dataclasses import dataclass
from typing import List

import numpy as np
import random


def random_tolerance(alpha) -> int:
    return int(random.expovariate(1 / alpha))


def random_interval_lambda(interval_lambda) -> int:
    return int(random.expovariate(interval_lambda))


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
    finish_service_time: int
    in_queue_time: List[int]
    out_queue_time: List[int]
    out_service_time: List[int]
    leave: bool
    part: int

    @staticmethod
    def gen(interval_lambda, alpha) -> 'Request':
        Request.GlobalTime += random_interval_lambda(interval_lambda)
        return Request(
            enter_time=Request.GlobalTime,
            priority=random_priority(),
            tolerance=random_tolerance(alpha),
            finish_service_time=None,
            in_queue_time=[],
            out_queue_time=[],
            out_service_time=[],
            leave=False,
            part=None,
        )

    def leave_time(self) -> int:
        return self.enter_time + self.tolerance

    def __hash__(self):
        return id(self)

    def __gt__(self, r2: 'Request'):
        if self.priority > r2.priority:
            return True
        elif self.priority == r2.priority and self.enter_time < r2.enter_time:
            return True
        return False

    def __str__(self):
        return "Time: %d, Priorty: %d, Tolerance: %d" % (self.enter_time, self.priority, self.tolerance)


class RequestHeap:
    def __init__(self):
        self.heap = [Request(-1, np.inf, 0, 0, [], [], [], False, None)]
        self.__ignore = set()
        self.ptr = 1

    def ignore(self, request: Request) -> None:
        self.__ignore.add(request)

    def __len__(self):
        return self.ptr - 1 - len(self.__ignore)

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
        self.heap.append(req)
        self.ptr += 1
        self.bubble_up()

    def top(self):
        while self.ptr > 1:
            req = self.heap[1]
            if req in self.__ignore:
                self.remove()
                self.__ignore.remove(req)
            else:
                return req
        return None

    def remove(self):
        self.ptr -= 1
        self.heap[1] = self.heap[self.ptr]
        self.bubble_down()
        return self.heap.pop()

    def pop(self):
        while self.top() in self.__ignore:
            self.remove()
        return self.remove()

    def is_empty(self):
        return self.ptr == 1


if __name__ == '__main__':
    requests = [
        Request.gen(1, 1),
        Request.gen(1, 1),
        Request.gen(1, 1),
        Request.gen(1, 1),
    ]
    heap = RequestHeap()
    heap.add(requests[0])
    heap.add(requests[1])
    heap.add(requests[2])
    heap.add(requests[3])

    print(heap.top())
    heap.ignore(heap.top())
    print(heap.top())
    heap.ignore(heap.top())
    print(heap.pop())
