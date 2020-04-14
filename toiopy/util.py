import threading
from typing import Callable
import math


def clamp(value: int, min_value: int, max_value: int) -> int:
    return math.ceil(max([min([value, max_value]), min_value]))


def set_timeout(task: Callable, delay_ms: int = 0):
    t = threading.Timer(delay_ms / 1000, task)
    t.start()
    t.join()
    return t


def clear_timeout(timer):
    timer.cancel()
