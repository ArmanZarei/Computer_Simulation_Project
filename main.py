import collections
import datetime
import random
from typing import List, Optional, Tuple
import numpy as np
import requests
from service import ServiceProvider
from timer import Timer
import matplotlib.pyplot as plt


class Pipeline:
    def __init__(self):
        self.timer = Timer.get_instance()

        N, interval_lambda, reception_rate, alpha = map(float, input().split())
        N = int(N)

        self.reception = ServiceProvider(
            1,
            [1/reception_rate],
            self.timer
        )

        self.services: List[ServiceProvider] = []
        for i in range(N):
            service_rates = list(map(float, input().split()))
            self.services.append(
                ServiceProvider(
                    len(service_rates),
                    [1/rate for rate in service_rates],
                    self.timer
                )
            )
        self.customers_ptr = 0
        self.customers = [requests.Request.gen(interval_lambda, alpha) for _ in range(1_000_000)]

    def __get_next_services(self) -> int:
        return min([service.get_next_event_time() for service in self.services])

    def __get_next_time(self) -> int:
        return min(
            np.inf if not self.customers_ptr != len(self.customers) else self.customers[self.customers_ptr].enter_time,
            self.reception.get_next_event_time(),
            self.__get_next_services()
        )

    # def print(self, customer: requests.Request):
    #     print(customer.enter_time, customer.out_service_time, customer.leave, customer.leave_time())

    def loop(self):
        now = datetime.datetime.now()
        print(now)
        while True:
            event = None
            next = self.__get_next_time()
            # print('-------')
            # print(self.timer.current_time)
            # print(next)
            # print(np.inf if not self.customers_ptr != len(self.customers) else self.customers[self.customers_ptr].enter_time)
            # print(self.reception.get_next_event_time())
            # print(self.__get_next_services())
            if next == np.inf:
                break
            self.timer.set_time(next)
            if self.customers_ptr != len(self.customers) and self.customers[self.customers_ptr].enter_time == next:
                # print('Add request to reception event')
                event = 1
                self.reception.add_request(self.customers[self.customers_ptr])
                self.customers_ptr += 1
            for service in self.services:
                if service.get_done_requests():
                    # print('Done request event')
                    event = 2
                if service.get_leave_requests():
                    # print('Service left')
                    event = 6
                # service_leave = service.get_leave_requests()
            reception_done = self.reception.get_done_requests()
            reception_leave = self.reception.get_leave_requests()
            if reception_done:
                # print('Reception Done event')
                event = 3
            # print(reception_leave)
            if reception_leave:
                # print('Reception left')
                event = 4
            for request in reception_done:
                who_to_send = random.randint(0, len(self.services) - 1)
                request.part = who_to_send
                self.services[who_to_send].add_request(request)
            if event is None:
                raise Exception
        for service in self.services + [self.reception]:
            left = service.container.left
            for req in left:
                req.leave = True
                if len(req.in_queue_time) != len(req.out_queue_time):
                    req.out_queue_time.append(req.leave_time())
                if len(req.in_queue_time) != len(req.out_service_time):
                    req.out_service_time.append(req.leave_time())
        # for request in self.customers:
        #     print(request.out_service_time, request.out_queue_time, request.in_queue_time)
        # print(self.timer.current_time)
        print((datetime.datetime.now()-now).total_seconds())
        self.calculate_metrics()

    def calculate_metrics(self):
        system_time = lambda request: request.out_service_time[-1] - request.enter_time
        for priority in [None] + [i for i in range(5)]:
            print(f'Average system time ({priority if priority is not None else "All"})',
                  self.calculate_average(priority, system_time))

        wait_time = lambda request: sum(request.out_queue_time) - sum(request.in_queue_time)
        for priority in [None] + [i for i in range(5)]:
            print(f'Average wait time ({priority if priority is not None else "All"})',
                  self.calculate_average(priority, wait_time))

        print(f'{sum([request.leave for request in self.customers])} people left the system')

        average_queues_length = self.calculate_average_queues_length()
        print(f'Reception average queue length', average_queues_length[0])
        for i in range(len(self.services)):
            print(f'Server {i} average queue length {average_queues_length[i + 1]}')

        self.timer.current_time += 1
        self.draw_plots()
        self.calculate_frequency()

    def calculate_average_queues_length(self) -> List[float]:
        reception_total = 0
        services_total = [0 for _ in range(len(self.services))]
        for request in self.customers:
            if len(request.out_queue_time):
                reception_total += request.out_queue_time[0] - request.in_queue_time[0]
            if len(request.out_queue_time) == 2:
                services_total[request.part] += request.out_queue_time[1] - request.in_queue_time[1]
        result = [
                     reception_total / self.timer.current_time
                 ] + [
                     (services_total[i] / self.timer.current_time) for i in range(len(self.services))
                 ]

        return result

        pass

    def calculate_average(self, priority: Optional[int], method):
        total = 0
        cnt = 0
        for request in self.customers:
            if priority and request.priority != priority:
                continue
            total += method(request)
            cnt += 1
        if not cnt:
            return 0
        return total / cnt

    def plot(self, name: str, data: List[int]):
        plt.hist(data, bins=100,)#, [i for i in range(len(data))])
        plt.title(name)
        plt.show()

    def partial_sum(self, data: List[int]):
        for i in range(1, len(data)):
            data[i] += data[i - 1]

    def draw_plots(self):
        reception_queue_length = [0 for _ in range(self.timer.current_time)]
        service_queue_length = [[0 for _ in range(self.timer.current_time)] for j in range(len(self.services))]
        for request in self.customers:
            # print(self.timer.current_time)
            # print(request.leave)
            # print(request.in_queue_time)
            # print(request.out_queue_time)
            # print(request.part)
            if len(request.in_queue_time):
                reception_queue_length[request.in_queue_time[0]] += 1
                reception_queue_length[request.out_queue_time[0]] -= 1
            if len(request.in_queue_time) == 2:
                service_queue_length[request.part][request.in_queue_time[1]] += 1
                service_queue_length[request.part][request.out_queue_time[1]] -= 1
        self.partial_sum(reception_queue_length)
        self.plot('Reception Queues length', reception_queue_length)
        for i in range(len(self.services)):
            self.partial_sum(service_queue_length[i])
            self.plot(f'Service {i} Queues length', service_queue_length[i])

    def calculate_frequency(self):
        system_times = [[] for _ in range(5)]
        wait_times = [[] for _ in range(5)]
        for request in self.customers:
            system_times[request.priority].append(
                sum(request.out_service_time) - sum(request.out_queue_time)
            )
            wait_times[request.priority].append(
                sum(request.out_queue_time) - sum(request.in_queue_time)
            )
        for priority in range(5):
            plt.hist(system_times[priority], bins=100)
            plt.title(f"System time frequency priority {priority}")
            plt.show()

        for priority in range(5):
            plt.hist(wait_times[priority], bins=100)
            plt.title(f"Wait time frequency priority {priority}")
            plt.show()


if __name__ == '__main__':
    pipeline = Pipeline()
    pipeline.loop()
