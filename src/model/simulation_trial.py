import math
import numpy as np


class SimulationPopulations:
    initial_populations: np.ndarray[float]
    growth_rates: np.ndarray[float]
    coefficients: np.ndarray[np.ndarray[float]]

    def __init__(self, initial_populations, growth_rates, coefficients) -> None:
        self.initial_populations = initial_populations
        self.growth_rates = growth_rates
        self.coefficients = coefficients


class SimulationAccuracy:
    euler_step: float
    max_time: int
    """How many timesteps should each simulation run for"""
    extinct_if_below: float

    def __init__(
        self,
        euler_step: float = 0.005,
        max_time: int = 200,
        extinct_if_below: float = 1e-10,
        goal_rounded_euler_step: float = 0.01,
    ) -> None:
        self.euler_step = euler_step
        self.max_time = max_time
        self.extinct_if_below = extinct_if_below
        self.goal_rounded_euler_step = goal_rounded_euler_step
        self.rounded_euler_step = self.steps_in_rounded() * self.euler_step

    def iterations(self):
        return math.ceil(self.max_time / self.euler_step)

    def steps_in_rounded(self) -> int:
        return max(1, int(self.goal_rounded_euler_step / self.euler_step))

    def rounded_iterations(self):
        return math.ceil(self.max_time / self.rounded_euler_step)


class SimulationTrial:
    index: int
    populations: SimulationPopulations
    accuracy: SimulationAccuracy

    def __init__(
        self,
        index: int,
        populations: SimulationPopulations,
        accuracy: SimulationAccuracy,
    ) -> None:
        self.index = index
        self.populations = populations
        self.accuracy = accuracy


class Generation(np.ndarray[float]):
    pass


class Generations(np.ndarray[Generation]):
    pass
