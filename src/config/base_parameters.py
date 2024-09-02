from abc import ABC
from random import Random
from typing import List
from uuid import UUID

from networkx import Graph


class SimulationEpochsConfig:
    epochs: int
    iterations: int
    threads: int
    """The number of CPU threads to use"""

    def __init__(
        self,
        epochs: int = 3,
        iterations: int = 10,
        threads: int = 1,
    ) -> None:
        self.epochs = epochs
        self.iterations = iterations
        self.threads = threads


class SimulationAccuracyConfig:
    hold_variable_per_trial: int
    """
    Each variable: euler_step, and extinct_if_below will be generated this number of times.
    Then each variable chosen will be joined with every other variable.

    Example:
        - hold_variable_per_trial: 3 # Means 3 numbers for each variable

        - euler_length: 1, 5, 2
        - extinct_if_below: 6, 7, 9
        
        Trials generated:
        [   (1,6),(1,7),(1,9),
            (5,6),(5,7),(5,9),
            (2,6),(2,7),(2,9)   ]
    """

    min_euler_step: float
    max_euler_step: float
    min_extinct_if_below: float
    max_extinct_if_below: float

    max_time: int

    def __init__(self) -> None:
        self.min_euler_step = 0.0005
        self.max_euler_step = 0.01
        self.min_extinct_if_below = 1e-8
        self.max_extinct_if_below = 1e-12
        self.max_time = 200
        self.hold_variable_per_trial = 10

    def get_max_time(self) -> int:
        return self.max_time

    def _gen_floats(self, random: Random, min: float, max: float) -> float:
        def generate():
            return random.random() * (max - min) + min

        return [generate() for _ in range(self.hold_variable_per_trial)]

    def gen_euler_steps(self, random: Random) -> List[float]:
        min = self.min_euler_step
        max = self.max_euler_step
        return self._gen_floats(random, min, max)

    def gen_extinct_if_belows(self, random: Random) -> List[float]:
        min = self.min_extinct_if_below
        max = self.max_extinct_if_below
        return self._gen_floats(random, min, max)


class BaseProgramParameters(ABC):
    accuracy: SimulationAccuracyConfig
    epochs: SimulationEpochsConfig

    @staticmethod
    def get_master_seed() -> UUID | None:
        """
        Notes:
        Is static in the sense that this should not have any state

        Returns:
        Any of the following:
            - Master seed: (UUID) used as the master seed for the program
            - (None) to signal that a random seed should be generated
        """
        return None

    @staticmethod
    def generate_networks(random: Random) -> List[Graph]:
        raise NotImplementedError("Not Implemented!")
