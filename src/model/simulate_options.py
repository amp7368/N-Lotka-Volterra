from numpy import ndarray
from typing import List


class SimulationPopulations:
    initial_populations: List[float]
    growth_rates: List[float]
    introduced_at: List[float]
    coefficients: List[List[float]]


class SimulationPlot:
    include_legend: bool
    linewidth: int
    round_to_ticks: int
    # Note this is in inches
    dim_x: float
    dim_y: float
    dpi: int

    def __init__(self) -> None:
        self.include_legend = True
        self.linewidth = 1
        self.round_to_ticks = 5000
        self.dim_x = 10.0
        self.dim_y = 10.0
        self.dpi = 400


class SimulationAccuracy:
    euler_step: float
    max_time: int
    extinct_if_below: float

    def __init__(self) -> None:
        self.euler_step = 0.005
        self.max_time = 200
        self.extinct_if_below = 1e-10

    def iterations(self):
        return int(self.max_time / self.euler_step)


class SimulationOptions:
    populations: SimulationPopulations
    plot: SimulationPlot
    accuracy: SimulationAccuracy

    def __init__(self) -> None:
        self.populations = SimulationPopulations()
        self.plot = SimulationPlot()
        self.accuracy = SimulationAccuracy()

    def __str__(self) -> str:
        return str(self.__dict__)


class Coefficients(ndarray[ndarray[float]]):
    pass


class Generation(ndarray[float]):
    pass


# type Generation = ndarray[float]


class Generations(ndarray[Generation]):
    pass
