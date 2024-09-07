from abc import ABC
from random import Random
from typing import List
from uuid import UUID

from networkx import Graph

from util.random_util import RandomMeshVariables, random_float, random_int


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


class SimulationAccuracyConfig(RandomMeshVariables):
    min_euler_step: float
    max_euler_step: float
    min_extinct_if_below: float
    max_extinct_if_below: float

    max_time: int

    def __init__(self) -> None:
        hold_variable = 3
        super(SimulationAccuracyConfig, self).__init__(hold_variable)
        self.min_euler_step = 0.01
        self.max_euler_step = 0.02
        self.min_extinct_if_below = 1e-8
        self.max_extinct_if_below = 1e-12
        self.max_time = 500

    def get_max_time(self) -> int:
        return self.max_time

    def gen_euler_steps(self, random: Random) -> List[float]:
        a = self.min_euler_step
        b = self.max_euler_step
        return self.gen_floats(random, a, b)

    def gen_extinct_if_belows(self, random: Random) -> List[float]:
        a = self.min_extinct_if_below
        b = self.max_extinct_if_below
        return self.gen_floats(random, a, b)


class BaseProgramParameters(RandomMeshVariables):
    accuracy: SimulationAccuracyConfig
    epochs: SimulationEpochsConfig

    def __init__(self, hold_variable=3) -> None:
        super().__init__(hold_variable)

    def get_master_seed(self) -> UUID | None:
        """
        Notes:
        Is static in the sense that this should not have any state

        Returns:
        Any of the following:
            - Master seed: (UUID) used as the master seed for the program
            - (None) to signal that a random seed should be generated
        """
        return None

    def generate_networks(self, random: Random) -> List[Graph]:
        raise NotImplementedError("Not Implemented!")
