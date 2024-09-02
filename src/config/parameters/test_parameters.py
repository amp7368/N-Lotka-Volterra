from random import Random
from typing import List, Tuple, override
from uuid import UUID

import networkx as nx
import numpy as np
from matplotlib import pyplot as plt
from networkx import (
    Graph,
    balanced_tree,
    binomial_tree,
    duplication_divergence_graph,
    navigable_small_world_graph,
    scale_free_graph,
)

from config.base_parameters import (
    BaseProgramParameters,
    SimulationAccuracyConfig,
    SimulationEpochsConfig,
)


class TestSettings:
    branching_factor: int
    height: int

    def __init__(self, branching_factor: int, height: int) -> None:
        self.branching_factor = branching_factor
        self.height = height


class GuassFactor:
    mean: float
    sigma: float
    min_value: float | None
    max_value: float | None

    def __init__(
        self,
        mean: float,
        sigma: float,
        min_value: float | None = None,
        max_value: float | None = None,
    ) -> None:
        self.mean = mean
        self.sigma = sigma
        self.min_value = min_value
        self.max_value = max_value


class TestParameters(BaseProgramParameters):
    # Metadata
    master_seed = None  # "fbd6924d-581c-40a3-9343-bb9da5162263"
    hold_variable_per_trial: int = 1

    # network structure
    min_branching_factor: int = 5
    max_branching_factor: int = 5
    min_height: int = 4
    max_height: int = 4

    # Node data
    min_population: float = 4
    max_population: float = 20

    percent_predator: float = 0.8
    min_growth_rate: float = -0.01
    max_growth_rate: float = 0.01

    # Relationships
    prey_coefficient: float = -0.01
    predator_coefficient: float = 0.010
    max_symbiotic_relationship: float = 0.0

    def __init__(self) -> None:
        super().__init__()
        self.accuracy = SimulationAccuracyConfig()
        self.accuracy.hold_variable_per_trial = 1
        self.epochs = SimulationEpochsConfig()

    @override
    def get_master_seed(self) -> UUID | None:
        if self.master_seed is None:
            return None
        return UUID(self.master_seed)

    def _generate_network(self, random: Random, settings: TestSettings) -> Graph:
        G: Graph = navigable_small_world_graph(
            10, seed=random.randint(0, int(1e20)), dim=2
        )

        # nx.draw(G)
        # plt.show()

        for node1, node2 in G.edges.keys():
            G.add_edge(node2, node1)
        # Edge Attributes
        for node1, node2 in G.edges.keys():
            edge = G.get_edge_data(u=node1, v=node2, default=None)
            reverse = G.get_edge_data(u=node2, v=node1, default=None)
            if edge is None:
                continue
            # Coefficients between nodes
            is_predator = random.random() < self.percent_predator
            if is_predator:
                edge["weight"] = random.random() * self.min_growth_rate
            else:
                edge["weight"] = random.random() * self.max_growth_rate
            # cap symbiotic relationships
            if reverse is not None and "weight" in reverse and reverse["weight"] > 0:
                edge["weight"] = min(edge["weight"], self.max_symbiotic_relationship)

        # Node Attributes
        for node_id, node in G.nodes.items():
            node["population"] = self.rand_float(
                random, self.min_population, self.max_population
            )

            preyness = 1
            predatorness = 1
            for neighbor in G.neighbors(node_id):
                weight = G.get_edge_data(node_id, neighbor)["weight"]
                if weight > 0:
                    predatorness += self.percent_predator
                else:
                    preyness += 1 - self.percent_predator

            # Create a self edge if one doesn't already exist
            if not G.has_edge(u=node_id, v=node_id):
                G.add_edge(node_id, node_id)
            self_edge = G.get_edge_data(u=node_id, v=node_id, default=None)
            # Set the grwoth rate of each node

            if predatorness == preyness and preyness != 0:
                if random.random() < 0.5:
                    predatorness += 1e-10
                else:
                    preyness += 1e-10
            if predatorness > preyness:
                percent_predator = 1 - (preyness / predatorness)
                mean = self.min_growth_rate * percent_predator
                sigma = min(abs(mean - self.min_growth_rate), abs(mean))
            elif predatorness < preyness:
                percent_prey = 1 - (predatorness / preyness)
                mean = self.max_growth_rate * percent_prey
                sigma = min(abs(mean - self.max_growth_rate), abs(mean))

            weight = random.gauss(mean, sigma)
            # print(f"mean {mean:0.5f} | sigma {sigma:.5f} = weight {weight:.5f}")
            self_edge["weight"] = weight

        return G

    @override
    def generate_networks(self, random: Random) -> List[Graph]:
        # Declare variables to meshgrid
        branching_factors: List[int] = self._gen_branching_factors(random)
        heights: List[int] = self._gen_heights(random)

        settings = np.meshgrid(branching_factors, heights)
        for i in range(len(settings)):
            settings[i] = settings[i].flatten()

        branching_factors, heights = settings

        networks = []
        for branching_factor, height in zip(*settings):
            settings = TestSettings(
                branching_factor=branching_factor,
                height=height,
            )
            graph: Graph = self._generate_network(random, settings)
            networks.append(graph)
        return networks

    def rand_float(self, random: Random, a: float, b: float):
        lower = min(a, b)
        upper = max(a, b)
        return random.random() * (upper - lower) + lower

    def _gen_floats(self, random: Random, min: float, max: float) -> float:
        return [self.rand_float() for _ in range(self.hold_variable_per_trial)]

    def _gen_ints(self, random: Random, min: int, max: int) -> float:
        def generate():
            return random.randrange(min, max + 1)

        return [generate() for _ in range(self.hold_variable_per_trial)]

    def _gen_branching_factors(self, random: Random):
        return self._gen_ints(
            random, self.min_branching_factor, self.max_branching_factor
        )

    def _gen_heights(self, random: Random):
        return self._gen_ints(random, self.min_height, self.max_height)
