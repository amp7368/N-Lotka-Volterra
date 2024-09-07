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


class RandomMeshVariables:
    hold_variable: int
    """
    Each variable: euler_step, and extinct_if_below will be generated this number of times.
    Then each variable chosen will be joined with every other variable.

    Example:
        - hold_variable: 3 # Means 3 numbers for each variable

        - euler_length: 1, 5, 2
        - extinct_if_below: 6, 7, 9
        
        Trials generated:
        [   (1,6),(1,7),(1,9),
            (5,6),(5,7),(5,9),
            (2,6),(2,7),(2,9)   ]
    """

    def __init__(self, hold_variable: int) -> None:
        self.hold_variable = hold_variable

    def gen_floats(self, random: Random, a: float, b: float) -> float:
        return [random_float(random, a, b) for _ in range(self.hold_variable)]

    def gen_ints(self, random: Random, a: int, b: int) -> float:
        return [random_int(random, a, b) for _ in range(self.hold_variable)]
