from enum import StrEnum
from model.simulate_options import SimulationAccuracy, SimulationPlot


# NetworkStructureType = StrEnum("uniform")


class UniformNetworkStructure:
    independence_ratio: int


type NetworkStructure = UniformNetworkStructure


class GeneratePopulations:
    species_count: int
    # Can be any of the values in GenerateNetworkType
    # - uniform,... TODO add more examples
    network_structure_type: str
    network_structure: NetworkStructure
    # network_coeff: NetworkCoefficients


class GenerateOptions:
    population: GeneratePopulations
    plot: SimulationPlot
    accuracy: SimulationAccuracy
