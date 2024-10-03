from random import Random
from typing import List, Tuple, override

import numpy as np
from networkx import Graph, powerlaw_cluster_graph

from config.base_parameters import (
    BaseProgramParameters,
    SimulationAccuracyConfig,
    SimulationEpochsConfig,
)
from config.parameters.powerlaw.powerlaw_trial_settings import PowerLawSettings
from config.settings_factor import FactorConstant, FactorGenerator, FactorRangeInt
from config.settings_generator import FactorRangeFloat, SettingsGenerator
from util.random_util import random_int


class PowerLawParameters(BaseProgramParameters):
    # network structure
    species_count: FactorGenerator[int]
    connection_m_perc: FactorGenerator[float]
    connection_p: FactorGenerator[float]

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
        super().__init__("powerlaw", "09c158c3-18f3-40a4-80fe-2b855bff538f")
        self.species_count = FactorRangeInt(10, 625)
        self.connection_m_perc = FactorRangeFloat(0, 1)
        self.connection_p = FactorRangeFloat(0, 1)

        self.percent_predator = FactorConstant(0.8)

        self.population_range = FactorConstant(FactorRangeFloat(4, 20))
        self.min_growth_rate = FactorRangeFloat(-0.05, -0.015)
        self.max_growth_rate = FactorRangeFloat(0.05, 0.015)

        self.prey_coefficient = FactorConstant(-0.01)
        self.predator_coefficient = FactorConstant(0.01)
        self.max_symbiotic_relationship = FactorConstant(0.0)

        self.accuracy = SimulationAccuracyConfig()
        self.epochs = SimulationEpochsConfig()

    def _generate_network(self, random: Random, settings: PowerLawSettings) -> Graph:
        G: Graph = powerlaw_cluster_graph(
            settings.species_count,
            m=settings.connection_m,
            p=settings.connection_p,
            seed=random_int(random),
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
        for i in range(self.gen_count()):
            chosen_settings: List[FactorGenerator] = [
                self.species_count,
                self.connection_m_perc,
                self.connection_p,
                self.percent_predator,
                self.population_range,
                self.min_growth_rate,
                self.max_growth_rate,
                self.prey_coefficient,
                self.max_symbiotic_relationship,
            ]
            chosen_settings = [sett.generate(random) for sett in chosen_settings]
            chosen_settings = PowerLawSettings(*chosen_settings)

            graph: Graph = self._generate_network(random, chosen_settings)
            networks.append((graph, chosen_settings))
        return networks
