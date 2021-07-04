from typing import List

import settings
import requests
import service
from metric import Metric

def get_next_time() -> int:
    pass

class Pipelnie:
    def __init__(self):
        self.metrics = Metric.get_instance()

        N, interval_lambda, paziresh_rate, alpha = map(float, input().split())

        self.services:List[service.ServiceProvider] = []
        for i in range(N):
            service_rates = map(float, input().split())
            self.services.append(
                service.ServiceProvider(
                    len(service_rates),
                    service_rates,

                )
            )
        settings.interval_lambda = interval_lambda
        settings.alpha = alpha

        self.customers = [requests.Request.gen() for _ in range(settings.number_of_customers)]


def main():
    metrics = Metric.get_instance()



    time = 0
    while True:
        next = get_next_time()
        if True:  # when simulation is Done
            break


if __name__ == '__main__':
    main()
