from abc import abstractmethod
from random import Random
from uuid import UUID

from networkx import Graph

from config.base_parameters import (
    BaseProgramParameters,
    SimulationAccuracyConfig,
    SimulationEpochsConfig,
)
from util.seed import Seed


class ProgramParametersApi:
    """Make this IMMUTABLE"""

    base: BaseProgramParameters

    master_seed: Seed
    """initial starting seed for any psuedorandom calculations"""

    epochs: SimulationEpochsConfig
    """How many simulations should be run and parallelization"""

    accuracy: SimulationAccuracyConfig
    """Configuration for each simulation."""

    def __init__(self, master_seed: UUID, base: BaseProgramParameters) -> None:
        self.base = base
        self.master_seed = Seed(master_seed)
        self.accuracy = base.accuracy
        self.epochs = base.epochs

    def get_master_seed(self) -> Seed:
        return self.master_seed

    @abstractmethod
    def generate_networks(self, random: Random) -> Graph:
        # Should be implemented in base. Not here
        return self.base.generate_networks(random)
