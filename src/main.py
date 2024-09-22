from datetime import datetime
from time import time
from typing import List

from analyze.analyze import analyze_trial
from config.load_parameters import load_arguments
from config.parameters_api import ProgramParametersApi
from model.simulation import SimulationSeries
from model.simulation_series_id import SimulationSeriesId
from model.simulation_trial import Generations, SimulationTrial
from model.simulation_util import simulate
from store.dbase import db
from store.entity.dparameters import DParameters
from store.init_db import init_db
from store.save.save_trial import save_trial
from util.write_simulation import write_generations, write_meta_csv

SHOULD_WRITE_SIMULATIONS: bool = False


def run_trial(
    trial: SimulationTrial,
    dparameters: DParameters,
    config: ProgramParametersApi,
    trial_identifier: str,
):
    generations: Generations = simulate(trial)
    drun = save_trial(dparameters, trial)
    analyze_trial(dparameters, drun, trial, generations)

    if not SHOULD_WRITE_SIMULATIONS:
        return

    seed = config.master_seed.uuid
    prefix = f"run/{seed}/"

    nodes_file = f"{prefix}{trial_identifier}_nodes_{seed}.json"
    edges_file = f"{prefix}{trial_identifier}_edges_{seed}.json"
    write_meta_csv(
        trial.populations.growth_rates,
        trial.populations.coefficients,
        nodes_file,
        edges_file,
    )
    file = f"{prefix}{trial_identifier}_generations_{seed}.csv"
    write_generations(generations, file)


def progress(config, epoch, iteration, trial, trials):
    epoch_progress = f"epoch {epoch}/{config.epochs.epochs-1}"
    iteration_progress = f"iter {iteration}/{config.epochs.iterations-1}"
    trial_progress = f"trial {trial.index}/{len(trials)-1}"
    print(f"Running {epoch_progress}, {iteration_progress}, {trial_progress}")


def main():
    init_db()
    start = time()
    date: str = datetime.now().strftime("%Yy-%Mm-%dd_%Hh-%Mm-%Ss")

    config: ProgramParametersApi = load_arguments()
    dparameters: DParameters = DParameters(config.get_master_seed().uuid, config.base)
    db.save(dparameters)

    # No real difference between an epoch and iteration atm
    for epoch in range(config.epochs.epochs):
        for iteration in range(config.epochs.iterations):
            simulation: SimulationSeries = SimulationSeries(
                config, SimulationSeriesId(epoch, iteration)
            )

            trials: List[SimulationTrial] = simulation.iteration_generate_trials()
            for trial in trials:
                progress(config, epoch, iteration, trial, trials)

                trial_identifier = f"{epoch:04d}ep-{iteration:04d}s-{trial.index:04d}t"
                run_trial(trial, dparameters, config, trial_identifier)

    print(f"Took {time() - start}s")


if __name__ == "__main__":
    main()
