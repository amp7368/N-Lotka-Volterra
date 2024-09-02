from typing import Mapping
import networkx as nx

from model.simulate_options import SimulationOptions


def convert(G: nx.Graph):
    options = SimulationOptions()
    node: nx.NodeView
    for node in G.nodes:
        print(node)

    # opulations: List[float]
    # growth_rates: List[float]
    # introduced_at: List[float]
    # coefficients: List[List[float]]


def main():
    G: nx.Graph = nx.balanced_tree(5, 5)

    convert(G)


if __name__ == "__main__":
    main()
