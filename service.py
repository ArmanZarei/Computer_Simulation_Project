from typing import Optional, List
from container import Container

from requests import Request
import numpy as np

from timer import Timer


class ServiceProvider:
    def __init__(self, services_count: int, exp_lambdas: List[float], timer: Timer):
        self.exp_lambdas = exp_lambdas
        self.requests = set()
        self.container = Container(timer)
        self.services: List[Optional[Request]] = [None for _ in range(services_count)]
        self.timer = timer
        self.busy_servies = 0

    def __get_random_service_time(self, service_idx):
        return int(np.random.exponential(self.exp_lambdas[service_idx]))

    def __get_random_service_idx(self):
        return np.random.choice(
            [
                service_idx
                for service_idx, service in enumerate(self.services)
                if service is None
            ]
        )

    def __assign_request_to_a_service(self):
        req = self.container.next_request(pop=True)
        req.out_queue_time.append(self.timer.current_time)
        service_idx = self.__get_random_service_idx()
        req.finish_service_time = (
            self.timer.current_time + self.__get_random_service_time(service_idx)
        )
        self.services[service_idx] = req

    def get_next_event_time(self):
        if self.busy_servies < len(self.services) and not self.container.is_empty():
            print("1")
            return self.timer.current_time
        services_earliest_time = min(
            [np.inf]
            + [
                req.finish_service_time if req is not None else np.inf
                for req in self.services
            ]
        )
        services_earliest_leave_time = min(
            [np.inf]
            + [
                req.enter_time + req.tolerance if req is not None else np.inf
                for req in self.services
            ]
        )

        return min(services_earliest_time, services_earliest_leave_time)

    def __try_to_assign(self):
        while self.busy_servies < len(self.services) and not self.container.is_empty():
            self.__assign_request_to_a_service()
            self.busy_servies += 1

    def get_done_requests(self):
        result = []
        for req_idx, req in enumerate(self.services):
            req: Request
            if req is None:
                continue
            if req.finish_service_time < self.timer.current_time:
                raise Exception()
            if req.finish_service_time > self.timer.current_time:
                continue
            result.append(req)
            req.out_service_time.append(self.timer.current_time)
            self.services[req_idx] = None
            self.busy_servies -= 1
        self.__try_to_assign()

        return result

    def get_leave_requests(self) -> List[Request]:
        result: List[Request] = []
        for req_idx, req in enumerate(self.services):
            if req is None or req.leave_time() > self.timer.current_time:
                continue
            result.append(req)
            self.requests.remove(req)
            self.services[req_idx] = None
            self.busy_servies -= 1
            req.leave = True
            req.out_service_time.append(self.timer.current_time)

        self.__try_to_assign()

        return result

    def add_request(self, req: Request):
        self.requests.add(req)
        req.in_queue_time.append(self.timer.current_time)
        self.container.add_request(req)
        self.__try_to_assign()
