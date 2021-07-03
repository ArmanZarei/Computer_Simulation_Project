import numpy as np

class Request:
    def __init__(self, time, priority, tolerance):
        self.time = time
        self.priority = priority
        self.tolerance = tolerance
    
    def __gt__(self, r2):
        if self.priority > r2.priority:
            return True
        elif self.priority == r2.priority and self.time < r2.time:
            return True
        return False
    
    def __str__(self):
        return "Time: %d, Priorty: %d, Tolerance: %d" % (self.time, self.priority, self.tolerance)

class RequestHeap:
    def __init__(self, size):
        self.heap = [None for _ in range(size + 1)]
        self.ptr = 1
        self.heap[0] = Request(-1, np.inf, 0)
    
    def swap(self, ptr1, ptr2):
        self.heap[ptr1], self.heap[ptr2] = self.heap[ptr2], self.heap[ptr1] 

    def bubble_up(self):
        ptr = self.ptr-1
        while self.heap[ptr] > self.heap[ptr//2]:
            self.swap(ptr, ptr//2)
            ptr = ptr//2
        
    def bubble_down(self):
        ptr = 1
        while True:
            if 2*ptr + 1 < self.ptr and self.heap[ptr] < self.heap[ptr*2 + 1]:
                tmp_ptr = 2*ptr + 1
                if self.heap[ptr*2] > self.heap[ptr*2 + 1]:
                    tmp_ptr = ptr*2
                self.swap(ptr, tmp_ptr)
                ptr = tmp_ptr
            elif 2*ptr < self.ptr and self.heap[ptr] < self.heap[ptr*2]:
                self.swap(ptr, ptr*2)
                ptr *= 2
            else:
                break

    def add(self, req: Request):
        self.heap[self.ptr] = req
        self.ptr += 1
        self.bubble_up()
    
    def top(self):
        return self.heap[1]
    
    def pop(self):
        top = self.top()
        self.ptr -= 1
        self.heap[1] = self.heap[self.ptr]
        self.bubble_down()

        return top

test_requests = [
    Request(5, 3, 0),
    Request(10, 3, 0),
    Request(3, 3, 0),
    Request(6, 3, 0),
    Request(7, 3, 0),
    Request(1, 3, 0),
    Request(12, 3, 0),
    Request(2, 3, 0),
    Request(3, 4, 0),
    Request(6, 4, 0),
    Request(7, 4, 0),
    Request(1, 4, 0),
]
req_heap = RequestHeap(len(test_requests))
for req in test_requests:
    req_heap.add(req)

for _ in range(len(test_requests)):
    print(req_heap.pop())
