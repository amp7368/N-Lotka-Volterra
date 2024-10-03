from abc import ABC, abstractmethod
from random import Random
from typing import List, override

from store.entity.danalysis_cname import get_column
from store.entity.danalysis_datapoint import DAnalysisDatapoint
from store.entity.drun import DRun


class FactorGenerator[R](ABC):
    typeId: str

    def __init__(self, type_id: str) -> None:
        self.typeId = type_id

    @abstractmethod
    def generate(self, random: Random) -> R:
        raise "Not implemented!"

    @abstractmethod
    def as_columns(self, run: DRun, prefix: str) -> List[DAnalysisDatapoint]:
        raise "Not implemented!"


class FactorRangeFloat(FactorGenerator[float]):
    min_val: float
    max_val: float

    def __init__(self, a: float, b: float) -> None:
        super().__init__("factor_range_float")
        self.min_val = min(a, b)
        self.max_val = max(a, b)

    @override
    def generate(self, random: Random) -> float:
        return random.uniform(self.min_val, self.max_val)

    @override
    def as_columns(self, run: DRun, prefix: str) -> List[DAnalysisDatapoint]:
        min_val_col = get_column(f"{prefix}.range(min)")
        max_val_col = get_column(f"{prefix}.range(max)")
        return [
            DAnalysisDatapoint(run, min_val_col, self.min_val),
            DAnalysisDatapoint(run, max_val_col, self.max_val),
        ]


class FactorRangeInt(FactorGenerator[int]):
    min_val: int
    max_val: int

    def __init__(self, a: int, b: int, inclusive=True) -> None:
        super().__init__("factor_range_int")
        self.min_val = min(a, b)
        self.max_val = max(a, b)
        if not inclusive:
            self.max_val -= 1

    @override
    def generate(self, random: Random) -> int:
        return random.randint(self.min_val, self.max_val)

    @override
    def as_columns(self, run: DRun, prefix: str) -> List[DAnalysisDatapoint]:
        min_val_col = get_column(f"{prefix}.range(min)")
        max_val_col = get_column(f"{prefix}.range(max)")
        return [
            DAnalysisDatapoint(run, min_val_col, self.min_val),
            DAnalysisDatapoint(run, max_val_col, self.max_val),
        ]


class FactorConstant[R](FactorGenerator[R]):
    val: R

    def __init__(self, val: R) -> R:
        super().__init__("factor_constant")
        self.val = val

    def generate(self, random: Random) -> R:
        return self.val

    @override
    def as_columns(self, run: DRun, prefix: str) -> List[DAnalysisDatapoint]:
        col = get_column(f"{prefix}.val")
        return [DAnalysisDatapoint(run, col, self.val)]
