from main import RequestHeap
import numpy as np


class ServiceProvider:
    def __init__(self, services_count, exp_lambdas, queue_max_size, timer):
        self.exp_lambdas = exp_lambdas
        self.queue = RequestHeap(queue_max_size)
        self.services = [None for _ in range(services_count)]
        self.timer = timer
        self.busy_servies = 0

    def __get_random_service_time(self, service_idx):
        return np.random.exponential(self.exp_lambdas[service_idx])
    
    def __get_random_service_idx(self):
        return np.random.choice([service_idx for service_idx, service in self.services if service is None])
    
    def __assign_request_to_a_service(self):
        req = self.queue.pop()
        service_idx = self.__get_random_service_idx()
        req.time = self.timer + self.__get_random_service_time(service_idx)
        self.services[service_idx] = req
    
    def get_next_event_time(self):
        queue_req = self.queue.top()
        queue_req_earliest_time = queue_req.time if queue_req is not None else np.inf
        services_earliest_time = min([req.time if req is not None else np.inf for req in self.services])

        return min(queue_req_earliest_time, services_earliest_time)

    def get_done_requests(self):
        result = []
        for req_idx, req in enumerate(self.services):
            if req is None or req.time < self.timer.now():
                continue
            result.append(req)
            self.services[req_idx] = None
            if not self.queue.is_empty():
                self.__assign_request_to_a_service()
            else:
                self.busy_servies -= 1
        
        return result

    def add_request(self, req):
        self.queue.add(req)
        if self.busy_servies < len(self.services):
            self.__assign_request_to_a_service()
            self.busy_servies += 1