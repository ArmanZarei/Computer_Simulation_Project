from dataclasses import dataclass
from typing import List

import numpy as np
import random


def random_tolerance(alpha) -> int:
    return int(np.random.exponential(alpha))


def random_interval_lambda(interval_lambda) -> int:
    return np.random.exponential(1 / interval_lambda)


def random_priority() -> int:
    x = random.random()
    if x < 0.5:
        return 0
    if x < 0.7:
        return 1
    if x < 0.85:
        return 2
    if x < 0.95:
        return 3
    return 4


@dataclass
class Request:
    """
    Attributes:
        enter_time: time that customer enter system
        priority: priority of customer [0, 4]
        tolerance: tolerance time of customer
        finish_service_time: this field is for ServiceProvider
        in_queue_time: list of times that request entered a queue
        out_queue_time: list of times that request exit a queue
        out_service_time: list of times that request service is done
        leave: True if customer left the system else False
        part: id of service
    """

    GlobalTime = 0

    enter_time: int
    priority: int
    tolerance: int
    finish_service_time: int
    in_queue_time: List[int]
    out_queue_time: List[int]
    out_service_time: List[int]
    leave: bool
    part: int

    @staticmethod
    def gen(interval_lambda, alpha) -> "Request":
        Request.GlobalTime += random_interval_lambda(interval_lambda)
        return Request(
            enter_time=int(Request.GlobalTime),
            priority=random_priority(),
            tolerance=random_tolerance(alpha),
            finish_service_time=None,
            in_queue_time=[],
            out_queue_time=[],
            out_service_time=[],
            leave=False,
            part=None,
        )

    def leave_time(self) -> int:
        return self.enter_time + self.tolerance

    def __hash__(self):
        return id(self)

    def __gt__(self, r2: "Request"):
        if self.priority > r2.priority:
            return True
        elif self.priority == r2.priority and self.enter_time < r2.enter_time:
            return True
        return False

    def __str__(self):
        return "Time: %d, Priorty: %d, Tolerance: %d" % (
            self.enter_time,
            self.priority,
            self.tolerance,
        )
