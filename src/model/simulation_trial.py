import math
import numpy as np

from model.simulation_series_id import SimulationSeriesId


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
        steps_in_rounded = max(1, math.ceil(goal_rounded_euler_step / euler_step))
        self.rounded_euler_step = steps_in_rounded * euler_step

    def iterations(self) -> int:
        return self.rounded_iterations() * self.steps_in_rounded()

    def steps_in_rounded(self) -> int:
        return int(self.rounded_euler_step // self.euler_step)

    def rounded_iterations(self) -> int:
        return int(self.max_time / self.rounded_euler_step)


class SimulationTrial:
    series_id: SimulationSeriesId
    index: int
    populations: SimulationPopulations
    accuracy: SimulationAccuracy
    settings: object

    def __init__(
        self,
        series_id: SimulationSeriesId,
        index: int,
        settings: object,
        populations: SimulationPopulations,
        accuracy: SimulationAccuracy,
    ) -> None:
        self.series_id = series_id
        self.index = index
        self.settings = settings
        self.populations = populations
        self.accuracy = accuracy


class Generation(np.ndarray[float]):
    pass


class Generations(np.ndarray[Generation]):
    pass


class FamilyLineage(np.ndarray[float]):
    pass
