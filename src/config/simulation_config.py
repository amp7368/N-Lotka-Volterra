from abc import abstractmethod
from random import Random
from uuid import UUID, uuid4

from networkx import Graph

from config.base_parameters import (
    BaseProgramParameters,
    SimulationAccuracyConfig,
    SimulationEpochsConfig,
)
from util.seed import Seed


class SimulationConfig:
    """Make this IMMUTABLE"""

    master_seed: Seed
    """initial starting seed for any psuedorandom calculations"""

    epochs: SimulationEpochsConfig
    """How many simulations should be run and parallelization"""

    accuracy: SimulationAccuracyConfig
    """Configuration for each simulation."""

    def __init__(self, config: BaseProgramParameters) -> None:
        self.master_seed = self._init_seed(config)
        self.generate_networks = config.generate_networks
        self.accuracy = config.accuracy
        self.epochs = config.epochs

    def _init_seed(self, config: BaseProgramParameters) -> Seed:
        seed: UUID | None = config.get_master_seed()
        if seed is not None:
            return Seed(seed)
        seed = uuid4()
        print(f"Master Seed of {seed} was chosen")
        return Seed(seed)

    def get_master_seed(self) -> Seed:
        return self.master_seed

    @abstractmethod
    def generate_networks(random: Random, network_size: int) -> Graph:
        # Should be implemented in __init__ by config
        raise "Not implemented!"
