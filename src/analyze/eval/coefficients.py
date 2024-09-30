from typing import List

import numpy as np

from analyze.eval_fn import Eval, EvalFn


def map_abs(fn: EvalFn):
    return lambda data: fn(np.abs(data))


def fn_median(data: np.ndarray):
    length = data.shape[0]
    out = np.zeros(shape=(length), dtype=data.dtype)
    for i in range(length):
        segment = data[i, :]
        segment = segment[segment.nonzero()]
        if len(segment) != 0:
            out[i] = np.median(segment)
    return out


def fn_std(d):
    return np.std(d, where=d != 0, axis=1)


def fn_mean(d):
    return np.mean(d, where=d != 0, axis=1)


def fn_sum(d):
    return np.sum(d, where=d != 0, axis=1)


def fn_count(d):
    return np.array(np.count_nonzero(d, axis=1), dtype=np.float64)


def coeff_evals() -> List[Eval]:
    nonzero_std = Eval(fn_std, "nonzero.std")
    nonzero_mean = Eval(fn_mean, "nonzero.mean")
    nonzero_median = Eval(fn_median, "nonzero.median")
    nonzero_sum = Eval(fn_sum, "nonzero.sum")
    nonzero_count = Eval(fn_count, "nonzero.count")

    abs_nonzero_std = Eval(map_abs(fn_std), "nonzero.abs.std")
    abs_nonzero_mean = Eval(map_abs(fn_mean), "nonzero.abs.mean")
    abs_nonzero_median = Eval(map_abs(fn_median), "nonzero.abs.median")
    abs_nonzero_sum = Eval(map_abs(fn_sum), "nonzero.abs.sum")

    return [
        nonzero_std,
        nonzero_mean,
        nonzero_median,
        nonzero_sum,
        nonzero_count,
        abs_nonzero_std,
        abs_nonzero_mean,
        abs_nonzero_median,
        abs_nonzero_sum,
    ]
