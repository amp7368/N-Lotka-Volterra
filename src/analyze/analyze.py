from typing import List, Tuple

import numpy as np

from analyze.cname import join_cname, join_description
from analyze.eval_fn import Eval, FloatArr, NamedCol
from analyze.scalar import scalar_eval
from model.simulation_trial import FamilyLineage, Generations, SimulationTrial
from model.simulation_util import GENERATIONS_DTYPE
from store.dbase import db
from store.entity.danalysis_datapoint import DAnalysisDatapoint
from store.entity.dparameters import DParameters
from store.entity.drun import DRun


class AnalysisPipeline[R]:
    """Represents a series of data transformations the input FloatArray to 'R'"""

    fns: List[Eval]
    out_fns: List[Eval[R]]

    def __init__(
        self,
        cname: str,
        out_fn: List[Eval[R]],
        *fns: Eval | List[Eval],
        desc: str = "",
    ) -> None:
        self.out_fns = out_fn
        self.fns = []
        for fn in fns:
            if isinstance(fn, list):
                self.fns.extend(fn)
            else:
                self.fns.append(fn)
        cname = join_cname(cname, *[fn.cname for fn in self.fns])
        desc = join_description(desc, *[fn.description for fn in self.fns])
        for fn in out_fn:
            fn.prepend(cname, desc)

    def eval(self, run: DRun, sess, arr: FloatArr) -> List[DAnalysisDatapoint]:
        data = arr
        for fn in self.fns:
            data = fn.calc(data)

        cols = []
        for fn in self.out_fns:
            val = fn.calc(data)
            dcname = fn.get_dcname(sess)
            cols.append(DAnalysisDatapoint(run, dcname, val))
        return cols


class DataAnalysis:
    cname: str
    desc: str
    pipelines: List[AnalysisPipeline]

    def __init__(self, cname: str, desc: str = "") -> None:
        self.cname = cname
        self.desc = desc
        self.pipelines = self.create_pipelines()

    def create_pipelines(self) -> List[AnalysisPipeline]:
        return [self.__pipeline()]
        dx1: Eval[FloatArr] = Eval(
            np.gradient, "dx(1)", "1st derivative - change in x over time."
        )
        dx2: List[Eval[FloatArr]] = [
            Eval(np.gradient, ""),
            Eval(np.gradient, "dx(2)", "2nd derivative - change in x over time^2."),
        ]
        fns = [[], dx1, dx2]
        return map(self.__pipeline, fns)

    def __pipeline(self, *fn: List[Eval[FloatArr]]) -> AnalysisPipeline:
        return AnalysisPipeline(self.cname, scalar_eval(), *fn, desc=self.desc)

    def eval(self, run: DRun, sess, data) -> List[DAnalysisDatapoint]:
        cols = []
        for pipeline in self.pipelines:
            cols.extend(pipeline.eval(run, sess, data))
        return cols


survival_days = DataAnalysis(
    "survival_days",
    desc="The number of days each species will survive for",
)
growth_rates = DataAnalysis(
    "growth_rates",
    desc="The rate populations will naturally increase/descrease in population",
)
initial_populations = DataAnalysis(
    "initial_populations",
    "The starting population for each species",
)


def analyze_trial(
    dparameters: DParameters,
    drun: DRun,
    trial: SimulationTrial,
    generations: Generations,
) -> None:
    # TODO use multiple timesteps (rather than just t=0) in a simulation

    if np.any(generations == -1):
        print("Failed ecosystem. Population to infinity")
        return

    survival_days_data = np.array(generations != 0)
    survival_days_data = survival_days_data.sum(axis=1, dtype=GENERATIONS_DTYPE)
    survival_days_data *= trial.accuracy.euler_step

    analysis: List[Tuple[DataAnalysis, FloatArr]] = [
        (survival_days, survival_days_data),
        (growth_rates, trial.populations.growth_rates),
        (initial_populations, trial.populations.initial_populations),
    ]

    for analyze, data in analysis:
        if not np.any(data):
            print("data has len of 0")
            return

    with db.sess() as sess:
        sess.add(drun)
        cols = trial.settings.as_columns(drun)
        sess.add_all(cols)

        for analyze, data in analysis:
            cols = analyze.eval(drun, sess, data)
            sess.add_all(cols)
        sess.commit()
