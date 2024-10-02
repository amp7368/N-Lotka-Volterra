from random import Random
from typing import List, override
from uuid import UUID

from networkx import Graph

from env.program_env import program_env
from util.random_util import RandomMeshVariables


class SimulationEpochsConfig:
    epochs: int
    iterations: int
    threads: int
    """The number of CPU threads to use"""

    def __init__(
        self,
        epochs: int = 50000,
        iterations: int = 10,
    ) -> None:
        self.epochs = epochs
        self.iterations = iterations
        self.threads = program_env.run.get_thread_count()


class SimulationAccuracyConfig(RandomMeshVariables):
    min_euler_step: float
    max_euler_step: float
    min_extinct_if_below: float
    max_extinct_if_below: float
    generate_count: int
    max_time: int

    def __init__(self) -> None:
        self.generate_count = 3
        self.min_euler_step = 0.01
        self.max_euler_step = 0.02
        self.min_extinct_if_below = 1e-8
        self.max_extinct_if_below = 1e-12
        self.max_time = 3000

    def get_max_time(self) -> int:
        return self.max_time

    @override
    def gen_count(self) -> int:
        return self.generate_count

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
    generate_count: int

    def __init__(self, typeName: str, typeId: str, generate_count=3) -> None:
        self.typeName = typeName
        self.typeId = UUID(typeId)
        self.generate_count = generate_count

    @override
    def gen_count(self) -> int:
        return self.generate_count

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
