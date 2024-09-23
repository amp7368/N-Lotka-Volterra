from random import Random
from typing import List, Tuple, override

import numpy as np
from networkx import Graph, navigable_small_world_graph

from config.base_parameters import (
    BaseProgramParameters,
    SimulationAccuracyConfig,
    SimulationEpochsConfig,
)
from config.parameters.small_world.small_world_trial_settings import SmallWorldSettings
from config.settings_factor import FactorConstant, FactorGenerator
from config.settings_generator import ConstantSettings, FactorRange, SettingsGenerator
from util.random_util import random_int


class TestParameters(BaseProgramParameters):
    # network structure
    network_dim: FactorGenerator[int]
    network_side_length: FactorGenerator[int]

    # Aggregate Node data
    percent_predator: FactorGenerator[float]

    # Node data
    population_range: SettingsGenerator[float]
    min_growth_rate: FactorGenerator[float]
    max_growth_rate: FactorGenerator[float]

    # Relationships
    prey_coefficient: FactorGenerator[float] = -0.01
    predator_coefficient: FactorGenerator[float] = 0.01
    max_symbiotic_relationship: FactorGenerator[float] = 0.0

    # Simulation Info
    epochs: SimulationEpochsConfig
    accuracy: SimulationAccuracyConfig

    def __init__(self) -> None:
        super().__init__()
        self.network_dim = FactorConstant(2)
        self.network_side_length = FactorConstant(10)

        self.percent_predator = FactorConstant(0.8)

        self.population_range = FactorConstant(FactorRange(4, 20))
        self.min_growth_rate = FactorRange(-0.05, -0.015)
        self.max_growth_rate = FactorRange(0.05, 0.015)

        self.prey_coefficient = FactorConstant(-0.01)
        self.predator_coefficient = FactorConstant(0.01)
        self.max_symbiotic_relationship = FactorConstant(0.0)

        self.accuracy = SimulationAccuracyConfig()
        self.epochs = SimulationEpochsConfig()

    def _generate_network(self, random: Random, settings: SmallWorldSettings) -> Graph:
        G: Graph = navigable_small_world_graph(
            settings.network_side_length,
            seed=random_int(random),
            dim=settings.network_dim,
        )

        # Verify relationships are not one way.
        # One-sided relationships are still possible if one node choses a coefficent close to 0
        for node1, node2 in G.edges.keys():
            G.add_edge(node2, node1)

        # Edge Attributes
        for node1, node2 in G.edges.keys():
            edge = G.get_edge_data(u=node1, v=node2, default=None)
            reverse = G.get_edge_data(u=node2, v=node1, default=None)

            # Coefficients between nodes
            if reverse is not None and "weight" in reverse:
                is_predator = reverse["weight"] > 0
            else:
                is_predator = random.random() < settings.percent_predator

            if is_predator:
                edge["weight"] = random.random() * settings.min_growth_rate
            else:
                edge["weight"] = random.random() * settings.max_growth_rate

        max_predatorness = 0
        max_preyness = 0
        for node_id in G.nodes:
            preyness = 0
            predatorness = 0
            for neighbor in G.neighbors(node_id):
                weight = G.get_edge_data(node_id, neighbor)["weight"]
                if weight > 0:
                    predatorness += weight  # self.percent_predator
                else:
                    preyness -= weight  # 1 - self.percent_predator
            max_preyness = max(preyness - predatorness, max_preyness)
            max_predatorness = max(predatorness - preyness, max_predatorness)

        # Node Attributes
        for node_id, node in G.nodes.items():
            node["population"] = settings.population_range.generate(random)
            preyness = 0
            predatorness = 0
            for neighbor in G.neighbors(node_id):
                weight = G.get_edge_data(node_id, neighbor)["weight"]
                if weight > 0:
                    predatorness += weight
                else:
                    preyness -= weight

            # Create a self edge if one doesn't already exist
            if not G.has_edge(u=node_id, v=node_id):
                G.add_edge(node_id, node_id)
            self_edge = G.get_edge_data(u=node_id, v=node_id)

            # Set the growth rate of each node
            if predatorness == preyness and preyness != 0:
                if random.random() < 0.5:
                    predatorness += 1e-30
                else:
                    preyness += 1e-30
            if predatorness > preyness:
                percent_predator = (predatorness - preyness) / (max_predatorness)
                mean = settings.min_growth_rate * percent_predator
                sigma = min(abs(settings.min_growth_rate - mean), abs(mean))
            elif predatorness < preyness:
                percent_prey = (preyness - predatorness) / max_preyness
                mean = settings.max_growth_rate * percent_prey
                sigma = min(abs(settings.max_growth_rate - mean), abs(mean))

            weight = random.gauss(mean, sigma)
            while np.sign(mean) != np.sign(weight):
                weight = random.gauss(mean, sigma)

            # print(f"mean {mean:0.5f} | sigma {sigma:.5f} = weight {weight:.5f}")
            self_edge["weight"] = weight

        return G

    @override
    def generate_networks(self, random: Random) -> List[Tuple[Graph, object]]:
        networks = []
        for i in range(self.hold_variable):
            chosen_settings: List[FactorGenerator] = [
                self.network_dim,
                self.network_side_length,
                self.percent_predator,
                self.population_range,
                self.min_growth_rate,
                self.max_growth_rate,
                self.prey_coefficient,
                self.max_symbiotic_relationship,
            ]
            chosen_settings = [sett.generate(random) for sett in chosen_settings]
            chosen_settings = SmallWorldSettings(*chosen_settings)

            graph: Graph = self._generate_network(random, chosen_settings)
            networks.append((graph, chosen_settings))
        return networks

    def _gen_branching_factors(self, random: Random):
        return self.gen_ints(
            random, self.min_branching_factor, self.max_branching_factor
        )

    def _gen_heights(self, random: Random):
        return self.gen_ints(random, self.min_height, self.max_height)
