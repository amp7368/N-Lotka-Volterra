from random import Random
from typing import List, override

from config.settings_factor import (
    FactorConstant,
    FactorGenerator,
    FactorRange,
)
from store.entity.danalysis_datapoint import DAnalysisDatapoint
from store.entity.drun import DRun


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


class SettingsGenerator[R](FactorGenerator[FactorGenerator[R]]):
    def __init__(self, type_id: str) -> None:
        super().__init__(type_id)

    @override
    def as_columns(self, run: DRun, prefix: str) -> List[DAnalysisDatapoint]:
        raise "Not implemented!"


class ConstantSettings[R](SettingsGenerator[R]):

    def __init__(self, val: R):
        super().__init__("constant_settings")
        self.val = val

    @override
    def generate(self, random: Random) -> SettingsGenerator[R]:
        return FactorConstant(self.val)


class RangeGenerator(SettingsGenerator[FactorRange]):
    center_mean: float
    center_std: float
    min_range_diff: float
    max_range_diff: float

    def __init__(
        self,
        center_mean: float,
        center_std: float,
        min_range_diff: float,
        max_range_diff: float,
    ) -> None:
        super().__init__("range_settings")
        self.center_mean = center_mean
        self.center_std = center_std
        self.min_range_diff = min_range_diff
        self.max_range_diff = max_range_diff

    @override
    def generate(self, random: Random) -> FactorRange:
        half_range_diff = random.uniform(self.max_range_diff, self.min_range_diff) / 2
        center = random.gauss(self.center_mean, self.center_std)
        lower = center - half_range_diff
        upper = center + half_range_diff
        return FactorRange(lower, upper)
