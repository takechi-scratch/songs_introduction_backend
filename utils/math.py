import math

def sigmoid(x: float, a: float = 1.0) -> float:
    return 1 / (1 + math.e ** -(a * x))
