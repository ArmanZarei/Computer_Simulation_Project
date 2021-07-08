import collections
import random
from typing import List, Optional
import numpy as np
import requests
from service import ServiceProvider
from metric import Metric
from timer import Timer


class Pipeline:
    def __init__(self):
        self.metrics = Metric.get_instance()
        self.timer = Timer.get_instance()

        N, interval_lambda, reception_rate, alpha = map(float, input().split())
        N = int(N)

        self.reception = ServiceProvider(
            1,
            [reception_rate],
            self.timer
        )

        self.services: List[ServiceProvider] = []
        for i in range(N):
            service_rates = list(map(float, input().split()))
            self.services.append(
                ServiceProvider(
                    len(service_rates),
                    service_rates,
                    self.timer
                )
            )

        self.customers_ptr = 0
        self.customers = [requests.Request.gen(interval_lambda, alpha) for _ in range(10_000_0)]

    def __get_next_services(self) -> int:
        return min([service.get_next_event_time() for service in self.services])

    def __get_next_time(self) -> int:
        return min(
            np.inf if not self.customers_ptr != len(self.customers) else self.customers[self.customers_ptr].enter_time,
            self.reception.get_next_event_time(),
            self.__get_next_services()
        )

    def loop(self):
        while True:
            next = self.__get_next_time()
            # print(self.timer.current_time, next)
            if next == np.inf:
                break
            self.timer.set_time(next)
            if self.customers_ptr != len(self.customers) and self.customers[self.customers_ptr].enter_time == next:
                self.reception.add_request(self.customers[self.customers_ptr])
                self.customers_ptr += 1
            for service in self.services:
                service_leave = service.get_leave_requests()
                done_requests = service.get_done_requests()
            reception_done = self.reception.get_done_requests()
            reception_leave = self.reception.get_leave_requests()

            for request in reception_done:
                who_to_send = random.randint(0, len(self.services) - 1)
                request.part = who_to_send
                self.services[who_to_send].add_request(request)
        self.calculate_metrics()

    def calculate_metrics(self):
        print(self.customers[0].__dict__)
        system_time = lambda request: request.out_service_time[-1] - request.enter_time
        for priority in [None] + [i for i in range(5)]:
            print(f'Average system time ({priority if priority else "All"})',
                  self.calculate_average(priority, system_time))

        wait_time = lambda request: sum(request.out_queue_time) - sum(request.in_queue_time)
        for priority in [None] + [i for i in range(5)]:
            print(f'Average wait time ({priority if priority else "All"})',
                  self.calculate_average(priority, wait_time))

        print(f'{sum([request.leave for request in self.customers])} people left the system')


    def calculate_average(self, priority: Optional[int], method):
        total = 0
        cnt = 0
        for request in self.customers:
            if priority and request.priority != priority:
                continue
            total += method(request)
            total += request.finish_service_time - request.enter_time
            cnt += 1
        return total / cnt


if __name__ == '__main__':
    pipeline = Pipeline()
    pipeline.loop()
