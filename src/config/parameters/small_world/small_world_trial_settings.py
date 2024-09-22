from typing import List

from config.settings_factor import FactorGenerator
from store.entity.danalysis_cname import get_column
from store.entity.danalysis_datapoint import DAnalysisDatapoint
from store.entity.drun import DRun


class SmallWorldSettings:
    # network structure
    network_dim: int
    network_side_length: int

    # Aggregate Node data
    percent_predator: float

    # Node data
    population_range: FactorGenerator[float]
    min_growth_rate: float
    max_growth_rate: float

    # Relationships
    prey_coefficient: float
    predator_coefficient: float
    max_symbiotic_relationship: float

    def __init__(
        self,
        network_dim,
        network_side_length,
        percent_predator,
        population_range,
        min_growth_rate,
        max_growth_rate,
        prey_coefficient,
        max_symbiotic_relationship,
    ) -> None:
        self.network_dim = int(network_dim)
        self.network_side_length = int(network_side_length)
        self.percent_predator = percent_predator
        self.population_range = population_range
        self.min_growth_rate = min_growth_rate
        self.max_growth_rate = max_growth_rate
        # self.prey_coefficient = prey_coefficient

    def as_columns(self, run: DRun) -> List[DAnalysisDatapoint]:
        constant_cols = [
            "network_dim",
            "network_side_length",
            "percent_predator",
            "min_growth_rate",
            "max_growth_rate",
        ]
        variable_cols = ["population_range"]

        datapoints = []
        for cname in constant_cols:
            col = self.__dict__[cname]
            datapoints.append(DAnalysisDatapoint(run, get_column(cname), col)),
        for cname in variable_cols:
            col = self.__dict__[cname]
            datapoints.extend(col.as_columns(run, cname))

        return datapoints
