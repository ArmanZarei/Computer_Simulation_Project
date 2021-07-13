from pipeline import Pipeline

if __name__ == "__main__":
    number_of_customers = 10_000
    number_of_services, interval_lambda, reception_rate, alpha = map(
        float, input().split()
    )
    number_of_services = int(number_of_services)
    services_rates = []
    for i in range(number_of_services):
        services_rates.append(list(map(float, input().split())))
    pipeline = Pipeline(
        services_rates, interval_lambda, reception_rate, alpha, number_of_customers, False
    )
    pipeline.loop()

    average_service_count = int(sum([len(x) for x in services_rates]) / len(services_rates))
    average_service_count = max(average_service_count, 1)

    while True:
        rate = float(input())
        if rate == -1:
            break
        services_rates = [[rate] * average_service_count for i in range(number_of_services)]

        Pipeline(
            services_rates, interval_lambda, reception_rate, alpha, number_of_customers, True
        ).loop()
