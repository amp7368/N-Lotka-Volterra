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
        # Populations
        network_graphs: List[Graph] = self.config.generate_networks(self.random)
        populations: List[SimulationPopulations] = [
            graph_to_matrix(graph) for graph in network_graphs
        ]
        # Accuracy
        accuracy_list = self.iteration_generate_settings()

        # Generate each trial for the generated network
        trials = []
        for population in populations:
            for accuracy in accuracy_list:
                index = len(trials)
                trial = SimulationTrial(index, population, accuracy)
                trials.append(trial)
        return trials

    def iteration_generate_settings(self) -> List[SimulationAccuracy]:
        accuracy: SimulationAccuracyConfig = self.config.accuracy
        # Get static accuracy variables
        max_time = accuracy.max_time
        # Generate rest of accuracy variables then mesh
        euler_steps: List[float] = accuracy.gen_euler_steps(self.random)
        extinct_if_belows: List[float] = accuracy.gen_extinct_if_belows(self.random)
        mesh = np.meshgrid(euler_steps, extinct_if_belows)
        mesh = [m.flatten() for m in mesh]

        accuracy_list = []
        for settings in zip(*mesh):
            accuracy = SimulationAccuracy(
                euler_step=settings[0],
                extinct_if_below=settings[1],
                max_time=max_time,
            )
            accuracy_list.append(accuracy)
        return accuracy_list
