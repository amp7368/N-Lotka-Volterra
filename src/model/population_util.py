import networkx as nx
import numpy as np

from model.simulation_trial import SimulationPopulations


def graph_to_matrix(G: nx.Graph) -> SimulationPopulations:
    node_count = G.number_of_nodes()
    initial_populations = np.zeros(shape=(node_count))
    data = [node for _, node in G.nodes(data=True)]
    for idx, node in enumerate(data):
        initial_populations[idx] = node["population"]

    growth_rates = np.zeros(shape=(node_count))
    coefficients = np.zeros(shape=(node_count, node_count))

    for idx1, node1 in enumerate(G.nodes):
        for idx2, node2 in enumerate(G.nodes):
            data = G.get_edge_data(u=node1, v=node2, default=None)
            if data is None:
                continue
            weight = data["weight"]
            if node1 == node2:
                growth_rates[idx1] = weight
            else:
                coefficients[idx1][idx2] = weight

    return SimulationPopulations(
        initial_populations,
        growth_rates,
        coefficients,
    )
