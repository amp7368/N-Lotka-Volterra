from random import Random
from typing import List, Tuple
from uuid import UUID

import numpy as np
from networkx import Graph

from config.base_parameters import SimulationAccuracyConfig
from config.parameters_api import ProgramParametersApi
from model.population_util import graph_to_matrix
from model.simulation_series_id import SimulationSeriesId
from model.simulation_trial import (
    SimulationAccuracy,
    SimulationPopulations,
    SimulationTrial,
)
from util.seed import Seed


class SimulationSeries:
    config: ProgramParametersApi

    # Per step random
    series_id: SimulationSeriesId
    random: Random

    def __init__(
        self, config: ProgramParametersApi, series_id: SimulationSeriesId
    ) -> None:
        self.config = config
        self.series_id = series_id
        self.__generate_random(series_id)

    def __generate_random(self, series_id: SimulationSeriesId) -> None:
        lst = series_id.to_bytes_list()
        master_seed: Seed = self.config.get_master_seed()
        self.random = master_seed.generate_random(*lst)

    def iteration_generate_trials(self) -> List[SimulationTrial]:
        # Populations
        network_graphs: List[Tuple[Graph, object]] = self.config.generate_networks(
            self.random
        )
        # Accuracy
        accuracy_list = self.iteration_generate_settings()

        # Generate each set of trials for each generated network
        trials = []
        for graph, settings in network_graphs:
            population: SimulationPopulations = graph_to_matrix(graph)
            for accuracy in accuracy_list:
                index = len(trials)
                trial = SimulationTrial(
                    self.series_id,
                    index,
                    settings,
                    population,
                    accuracy,
                )
                trials.append(trial)
        return trials

    def iteration_generate_settings(self) -> List[SimulationAccuracy]:
        accuracy: SimulationAccuracyConfig = self.config.accuracy
        # Get static accuracy variables
        max_time = accuracy.max_time
        # Generate rest of accuracy variables then mesh
        euler_steps: List[float] = accuracy.gen_euler_steps(self.random)
        extinct_if_belows: List[float] = accuracy.gen_extinct_if_belows(self.random)

        accuracy_list = []
        for settings in zip(euler_steps, extinct_if_belows):
            accuracy = SimulationAccuracy(
                euler_step=settings[0],
                extinct_if_below=settings[1],
                max_time=max_time,
            )
            accuracy_list.append(accuracy)
        return accuracy_list
