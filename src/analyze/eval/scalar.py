from typing import List

import numpy as np

from analyze.eval_fn import Eval
from model.simulation_trial import FamilyLineage


def scalar_eval() -> List[Eval[float]]:
    quartiles = map(eval_quartile, [0.125, 0.25, 0.75, 0.875])
    std = Eval(np.std, "std")
    mean = Eval(np.mean, "mean")
    median = Eval(np.median, "median")
    sum = Eval(np.sum, "sum")
    return [*quartiles, std, mean, median, sum]


def eval_quartile(n: float) -> Eval:
    def quartile(family: FamilyLineage):
        return np.quantile(family, n)

    return Eval(quartile, f"quartile({n})")
