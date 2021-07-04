import settings
import requests


def get_next_time() -> int:
    pass


def main():
    N, interval_lambda, paziresh_rate, alpha = map(float, input().split())
    for i in range(N):
        service_rates = map(float, input().split())
    settings.interval_lambda = interval_lambda
    settings.alpha = alpha

    customers = [requests.Request.gen() for _ in range(settings.number_of_customers)]

    time = 0
    while True:
        next = get_next_time()
        if True:  # when simulation is Done
            break


if __name__ == '__main__':
    main()
