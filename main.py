import random
from typing import List
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

        self.customers = list(
            reversed([requests.Request.gen(interval_lambda, alpha) for _ in range(5)])
        )

    def __get_next_services(self) -> int:
        return min([service.get_next_event_time() for service in self.services])

    def __get_next_time(self) -> int:
        return min(
            np.inf if not len(self.customers) else self.customers[-1].enter_time,
            self.reception.get_next_event_time(),
            self.__get_next_services()
        )

    def loop(self):
        while True:
            next = self.__get_next_time()
            print(self.timer.current_time, next)
            if next == np.inf:
                break
            self.timer.set_time(next)
            if len(self.customers) and self.customers[-1].enter_time == next:
                self.reception.add_request(self.customers.pop(-1))
            service_leave = service.get_leave_requests()
            for service in self.services:
                done_requests = service.get_done_requests()
            reception_done = self.reception.get_done_requests()
            reception_leave = self.reception.get_leave_requests()

            for request in reception_done:
                who_to_send = random.randint(0, len(self.services) - 1)
                self.services[who_to_send].add_request(request)


if __name__ == '__main__':
    pipeline = Pipeline()
    pipeline.loop()
