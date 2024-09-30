from typing import Callable, Tuple

import numpy as np
from sqlalchemy.orm import Session

from analyze.cname import join_cname, join_description
from store.entity.danalysis_cname import get_column
from store.entity.danalysis_datapoint import DAnalysisColumnName

type FloatArr = np.ndarray[float]
type EvalFn[R] = Callable[[FloatArr], R]
type ArrayEvalFn = EvalFn[FloatArr]
type ScalarEvalFn = EvalFn[float]

type NamedCol[R] = Tuple[str, R]


class Eval[R]:
    cname: str
    description: str
    dcname: DAnalysisColumnName | None
    calc: EvalFn[R]

    def __init__(self, fn: EvalFn[R], cname: str, desc: str = "") -> None:
        self.cname = cname
        self.description = desc
        self.calc = fn
        self.dcname = None

    def prepend(self, prefix_cname: str, prefix_desc: str) -> None:
        self.cname = join_cname(prefix_cname, self.cname)
        self.description = join_description(prefix_desc, self.description)

    def get_dcname(self, sess: Session):
        if self.dcname is None:
            self.dcname = get_column(self.cname, self.description)
        if self.dcname not in sess:
            sess.add(self.dcname)
        return self.dcname
