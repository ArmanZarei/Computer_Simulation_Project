from typing import Union, Any


class Metric:
    __metric = None

    system_time = [
        'system time 0',
        'system time 1',
        'system time 2',
        'system time 3',
        'system time 4',
    ]
    system_time_all = 'system time all'

    wait_time = [
        'wait time 0',
        'wait time 1',
        'wait time 2',
        'wait time 3',
        'wait time 4',
    ]
    wait_time_all = 'wait time all'

    leave = 'leave'

    def __init__(self):
        if Metric.__metric is not None:
            raise Exception('Call get_instance()')
        self.__data = {}

    def increment(self, key: str, value: Union[int, float]):
        if key not in self.__data:
            self.__data[key] = 0, 0
        self.__data[key] = (value, self.__data[key][1] + 1)

    def put(self, key: str, value: Any):
        if key not in self.__data:
            self.__data[key] = []
        self.__data[key].append(value)

    @staticmethod
    def get_instance():
        if not Metric.__metric:
            Metric.__metric = Metric()
        return Metric.__metric
