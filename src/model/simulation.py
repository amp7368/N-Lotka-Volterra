import hashlib
from random import Random
from typing import List

import numpy as np
from networkx import Graph

from config.base_parameters import SimulationAccuracyConfig
from config.simulation_config import SimulationConfig
from model.population_util import graph_to_matrix
from model.simulation_trial import (
    SimulationAccuracy,
    SimulationPopulations,
    SimulationTrial,
)
from util.seed import Seed

MAX_SEED_BYTES = 64

from uuid import UUID, uuid4


class Simulation:
    seeder: Seed
    config: SimulationConfig

    # Per step random
    random: Random

    def __init__(self, config: SimulationConfig, epoch: int) -> None:
        self.__generate_seed(config, epoch)
        self.config = config

    def __generate_seed(self, config: SimulationConfig, epoch: int) -> None:
        epoch_bytes = epoch.to_bytes(MAX_SEED_BYTES, "big")
        self.seeder = config.get_master_seed().generate_seed(epoch_bytes)

    def prepare_iteration(self, iteration: int) -> None:
        # Use the seeder to seed a new PRNG
        self.random = self.seeder.generate_random()

    def iteration_generate_trials(self) -> List[SimulationTrial]:
        accuracy: SimulationAccuracyConfig = self.config.accuracy

        # Populations
        network_graphs: List[Graph] = self.config.generate_networks(self.random)
        populations: List[SimulationPopulations] = [
            graph_to_matrix(graph) for graph in network_graphs
        ]

        # Get static accuracy variables
        max_time = accuracy.max_time
        # Generate rest of accuracy variables then mesh
        euler_steps: List[float] = accuracy.gen_euler_steps(self.random)
        extinct_if_belows: List[float] = accuracy.gen_extinct_if_belows(self.random)
        chosen_settings = np.meshgrid(euler_steps, extinct_if_belows)
        for i in range(len(chosen_settings)):
            chosen_settings[i] = chosen_settings[i].flatten()

        trials = []
        # Generate each trial for the generated network
        index: int = 0
        for population in populations:
            for euler_step, extinct_if_below in zip(*chosen_settings):
                accuracy = SimulationAccuracy(
                    euler_step=euler_step,
                    extinct_if_below=extinct_if_below,
                    max_time=max_time,
                )
                trial = SimulationTrial(index, population, accuracy)
                trials.append(trial)
                index += 1
        return trials
