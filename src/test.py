from random import random

import networkx as nx
import numpy as np

from model.simulate_options import SimulationOptions, SimulationPopulations
from model.write_simulation import write_file


class TestNode:
    population: float
    introduced_at: int


def graph_to_matrix(G: nx.Graph):
    node_count = G.number_of_nodes()
    introduced_at = np.zeros(shape=(node_count))
    initial_populations = np.zeros(shape=(node_count))
    for idx, node in G.nodes(data=True):
        node: dict
        initial_populations[idx] = node["population"]
        node_introduced_at = node.get("introduced_at", 0)
        introduced_at[idx] = node_introduced_at

    growth_rates = np.zeros(shape=(node_count))
    coefficients = np.zeros(shape=(node_count, node_count))

    for node1 in G.nodes:
        for node2 in G.nodes:
            data = G.get_edge_data(u=node1, v=node2, default=None)
            if data is None:
                continue
            weight = data["weight"]
            if node1 == node2:
                growth_rates[node1] = weight
            else:
                coefficients[node1][node2] = weight

    pops = SimulationPopulations()
    pops.coefficients = coefficients
    pops.growth_rates = list(growth_rates)
    pops.initial_populations = list(initial_populations)
    pops.introduced_at = list(introduced_at)

    options = SimulationOptions()
    options.populations = pops
    write_file(options, "generated_config.json")


def main():
    G: nx.Graph = nx.balanced_tree(4, 4)

    # Node Attributes
    for node_id, node in G.nodes.items():
        node["population"] = random() * 1000
        node["introduced_at"] = 0

        # Create a self edge if one doesn't already exist
        if not G.has_edge(u=node_id, v=node_id):
            G.add_edge(node_id, node_id)
        self_edge = G.get_edge_data(u=node_id, v=node_id, default=None)
        # Set the grwoth rate of each node
        self_edge["weight"] = (random() - 0.5) * 0.01

    # Edge Attributes
    for node1 in G.nodes:
        for node2 in G.nodes:
            edge = G.get_edge_data(u=node1, v=node2, default=None)
            if edge is None:
                continue
            # Coefficients between nodes
            edge["weight"] = (random() - 0.5) * 0.001

    graph_to_matrix(G)


if __name__ == "__main__":
    main()
