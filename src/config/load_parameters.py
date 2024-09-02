from config.parameters.test_parameters import TestParameters
from config.simulation_config import SimulationConfig


def load_arguments() -> SimulationConfig:
    parameters = TestParameters()
    return SimulationConfig(parameters)
