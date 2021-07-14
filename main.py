from pipeline import Pipeline

if __name__ == "__main__":
    number_of_customers = 10_000_000
    number_of_services, interval_lambda, reception_rate, alpha = map(
        float, input().split()
    )
    number_of_services = int(number_of_services)
    services_rates = []
    for i in range(number_of_services):
        services_rates.append(list(map(float, input().split())))
    pipeline = Pipeline(
        services_rates, interval_lambda, reception_rate, alpha, number_of_customers, False, True
    )
    pipeline.loop()

    result = []
    queues_length = []
    step = n = 10
    while n < step * 100:
        print(n)
        pipeline = Pipeline(
            services_rates, interval_lambda, reception_rate, alpha, n, False, False
        )
        pipeline.loop()
        queues_length.append(pipeline.calculate_average_queues_length())
        n += step
    x = []
    for i in range(1, len(queues_length)):
        cur = queues_length[i]
        last = queues_length[i - 1]
        x.append(
            max([abs(cur[j] - last[j]) / last[j] if last[j] else 0 for j in range(len(queues_length[i]))])
        )
    mean = sum(x) / len(x)
    for i in range(len(x)):
        x[i] = abs(x[i] - mean)
    x = list(sorted(x))
    x = x[len(x) // 4:3 * len(x) // 4]
    diff = [x[i - 1] - x[i] for i in range(1, len(x))]
    a = sum(diff) / len(diff)
    v0s = [x[j] + j * a for j in range(len(x))]
    v0 = sum(v0s) / len(v0s)
    t = (0.05 - v0) / a
    print(f'Number of customers for accuracy of 95% is {step + t * step}')

    average_service_count = int(sum([len(x) for x in services_rates]) / len(services_rates))
    average_service_count = max(average_service_count, 1)

    while True:
        rate = float(input())
        if rate == -1:
            break
        services_rates = [[rate] * average_service_count for i in range(number_of_services)]

        Pipeline(
            services_rates, interval_lambda, reception_rate, alpha, number_of_customers, True, True
        ).loop()
