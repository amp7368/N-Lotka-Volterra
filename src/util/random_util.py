from abc import ABC, abstractmethod
from random import Random


def random_int(random: Random, a: int | None = None, b: int | None = None):
    if a is None and b is None:
        return random.randint(0, int(1e50))

    lower = min(a, b)
    upper = max(a, b)
    return random.randrange(lower, upper + 1)


def random_float(random: Random, a: float, b: float):
    lower = min(a, b)
    upper = max(a, b)
    return random.random() * (upper - lower) + lower


class RandomMeshVariables(ABC):
    @abstractmethod
    def gen_count(self) -> int:
        raise Exception("Not implemented!")

    def gen_floats(self, random: Random, a: float, b: float) -> float:
        return [random_float(random, a, b) for _ in range(self.gen_count())]

    def gen_ints(self, random: Random, a: int, b: int) -> float:
        return [random_int(random, a, b) for _ in range(self.gen_count())]
