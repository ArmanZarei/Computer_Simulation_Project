import datetime
import random
from typing import List, Optional

import matplotlib.pyplot as plt
import numpy as np

import requests
from service import ServiceProvider
from timer import Timer


class Pipeline:
    """
    Attributes:
        timer: global timer instance
        reception: reception ServiceProvider
        services: list of services ServiceProvider
        customers: list of customers
        customers_ptr: pointer to first customer that has not been arrived yet

    """

    def __init__(
            self,
            services_rate: List[List[float]],
            interval_lambda: float,
            reception_rate: float,
            alpha: float,
            number_of_customers: int,
            just_queue_length: bool
    ):
        """

        Args:
            services_rate: list of service rate of each service
            interval_lambda: rate of enter interval
            reception_rate: rate of reception
            alpha: rate of tolerance
            number_of_customers: number of customers
            just_queue_length: if True just plot queues length
        """
        self.just_queue_length = just_queue_length
        self.timer = Timer.get_instance(reset=True)
        self.reception = ServiceProvider(1, [1 / reception_rate], self.timer)
        self.services: List[ServiceProvider] = []
        for i in range(len(services_rate)):
            self.services.append(
                ServiceProvider(
                    len(services_rate[i]),
                    [1 / rate for rate in services_rate[i]],
                    self.timer,
                )
            )
        self.customers_ptr = 0
        requests.Request.GlobalTime = 0
        self.customers = [
            requests.Request.gen(interval_lambda, alpha)
            for _ in range(number_of_customers)
        ]

    def __get_next_services(self) -> int:
        return min([service.get_next_event_time() for service in self.services])

    def __get_next_time(self) -> int:
        return min(
            np.inf
            if not self.customers_ptr != len(self.customers)
            else self.customers[self.customers_ptr].enter_time,
            self.reception.get_next_event_time(),
            self.__get_next_services(),
        )

    def loop(self):
        now = datetime.datetime.now()
        print(now)
        while True:
            next = self.__get_next_time()
            if next == np.inf:
                break
            self.timer.set_time(next)
            # new customer enter the system
            if (
                    self.customers_ptr != len(self.customers)
                    and self.customers[self.customers_ptr].enter_time == next
            ):
                self.reception.add_request(self.customers[self.customers_ptr])
                self.customers_ptr += 1
            for service in self.services:
                # service done
                service.get_done_requests()
                # service's customers left
                service.get_leave_requests()
                # reception done
            reception_done = self.reception.get_done_requests()
            # reception's customers left
            self.reception.get_leave_requests()
            # send customers from reception to services
            for request in reception_done:
                who_to_send = random.randint(0, len(self.services) - 1)
                request.part = who_to_send
                self.services[who_to_send].add_request(request)
        # set in/out queue/service for customers who left the system
        for service in self.services + [self.reception]:
            left = service.container.left
            for req in left:
                req.leave = True
                if len(req.in_queue_time) != len(req.out_queue_time):
                    req.out_queue_time.append(req.leave_time())
                if len(req.in_queue_time) != len(req.out_service_time):
                    req.out_service_time.append(req.leave_time())
        self.timer.current_time += 1
        if self.just_queue_length:
            self.plot_queue_length()
        else:
            print(
                f"Simulation takes {(datetime.datetime.now() - now).total_seconds()} seconds"
            )
            self.calculate_metrics()

    def average_queue_length(self):
        average_queues_length = self.calculate_average_queues_length()
        print(f"Reception average queue length", average_queues_length[0])
        for i in range(len(self.services)):
            print(f"Server {i} average queue length {average_queues_length[i + 1]}")

    def plot_queue_length(self):
        self.average_queue_length()
        sum_of_queue_length = [0 for _ in range(self.timer.current_time)]
        reception_queue_length = [0 for _ in range(self.timer.current_time)]
        service_queue_length = [
            [0 for _ in range(self.timer.current_time)]
            for j in range(len(self.services))
        ]
        for request in self.customers:
            if len(request.in_queue_time):
                reception_queue_length[request.in_queue_time[0]] += 1
                reception_queue_length[request.out_queue_time[0]] -= 1
                sum_of_queue_length[request.in_queue_time[0]] += 1
                sum_of_queue_length[request.out_queue_time[0]] -= 1

            if len(request.in_queue_time) == 2:
                service_queue_length[request.part][request.in_queue_time[1]] += 1
                service_queue_length[request.part][request.out_queue_time[1]] -= 1
                sum_of_queue_length[request.in_queue_time[1]] += 1
                sum_of_queue_length[request.out_queue_time[1]] -= 1
        self.partial_sum(sum_of_queue_length)
        self.plot("Sum of queues length", sum_of_queue_length)
        self.partial_sum(reception_queue_length)
        self.plot("Reception Queues length", reception_queue_length)
        for i in range(len(self.services)):
            self.partial_sum(service_queue_length[i])
            self.plot(f"Service {i} Queues length", service_queue_length[i])

    def calculate_metrics(self):
        system_time = lambda request: request.out_service_time[-1] - request.enter_time
        for priority in [None] + [i for i in range(5)]:
            print(
                f'Average system time ({priority if priority is not None else "All"})',
                self.calculate_average(priority, system_time),
            )

        wait_time = lambda request: sum(request.out_queue_time) - sum(
            request.in_queue_time
        )
        for priority in [None] + [i for i in range(5)]:
            print(
                f'Average wait time ({priority if priority is not None else "All"})',
                self.calculate_average(priority, wait_time),
            )

        print(
            f"{sum([request.leave for request in self.customers])} people left the system"
        )

        self.average_queue_length()

        self.draw_plots()
        self.calculate_frequency()

    def calculate_average_queues_length(self) -> List[float]:
        reception_total = 0
        services_total = [0 for _ in range(len(self.services))]
        for request in self.customers:
            if len(request.out_queue_time):
                reception_total += request.out_queue_time[0] - request.in_queue_time[0]
            if len(request.out_queue_time) == 2:
                services_total[request.part] += (
                        request.out_queue_time[1] - request.in_queue_time[1]
                )
        result = [reception_total / self.timer.current_time] + [
            (services_total[i] / self.timer.current_time)
            for i in range(len(self.services))
        ]

        return result

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
        number_of_bins = 100
        new_data = [0 for i in range(number_of_bins)]
        cnt = [0 for i in range(number_of_bins)]
        for i in range(len(data)):
            idx = i * number_of_bins // len(data)
            new_data[idx] += data[i]
            cnt[idx] += 1
        for i in range(number_of_bins):
            new_data[i] /= cnt[i]
        plt.hist(
            x=[i for i in range(len(new_data))],
            weights=new_data,
            bins=number_of_bins,
            edgecolor="w",
        )  # , [i for i in range(len(data))])
        plt.title(name)
        plt.show()

    def partial_sum(self, data: List[int]):
        for i in range(1, len(data)):
            data[i] += data[i - 1]

    def draw_plots(self):
        in_system_count = [0 for _ in range(self.timer.current_time)]
        reception_queue_length = [0 for _ in range(self.timer.current_time)]
        service_queue_length = [
            [0 for _ in range(self.timer.current_time)]
            for j in range(len(self.services))
        ]
        for request in self.customers:
            in_system_count[request.out_service_time[-1]] -= 1
            in_system_count[request.in_queue_time[0]] += 1
            if len(request.in_queue_time):
                reception_queue_length[request.in_queue_time[0]] += 1
                reception_queue_length[request.out_queue_time[0]] -= 1
            if len(request.in_queue_time) == 2:
                service_queue_length[request.part][request.in_queue_time[1]] += 1
                service_queue_length[request.part][request.out_queue_time[1]] -= 1
        self.partial_sum(in_system_count)
        self.plot("In system count", in_system_count)
        self.partial_sum(reception_queue_length)
        self.plot("Reception Queues length", reception_queue_length)
        for i in range(len(self.services)):
            self.partial_sum(service_queue_length[i])
            self.plot(f"Service {i} Queues length", service_queue_length[i])

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
            plt.hist(system_times[priority], bins=100, edgecolor="w")
            plt.title(f"System time frequency priority {priority}")
            plt.show()

        for priority in range(5):
            plt.hist(wait_times[priority], bins=100, edgecolor="w")
            plt.title(f"Wait time frequency priority {priority}")
            plt.show()
