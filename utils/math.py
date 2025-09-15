import math


def sigmoid(x: float, a: float = 1.0) -> float:
    return 1 / (1 + math.e ** -(a * x))


def calc_a(x):
    print(x)
    print(math.log(1 / 99) / -x)
    return math.log(1 / 99) / -x
