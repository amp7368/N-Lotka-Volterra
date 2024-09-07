from typing import List
from config.load_parameters import load_arguments
from config.simulation_config import SimulationConfig
from model.simulation import Simulation
from model.simulation_trial import SimulationTrial
from model.simulation_util import simulate
from util.write_simulation import write_generations, write_meta_csv

from datetime import datetime
from time import time

SHOULD_WRITE_SIMULATIONS: bool = False


def run_trial(trial: SimulationTrial, config: SimulationConfig, trial_identifier: str):
    generations = simulate(trial)
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

    if SHOULD_WRITE_SIMULATIONS:
        file = f"{prefix}{trial_identifier}_generations_{seed}.csv"
        write_generations(generations, file)


def progress(config, epoch, iteration, trial, trials):
    epoch_progress = f"epoch {epoch}/{config.epochs.epochs-1}"
    iteration_progress = f"iter {iteration}/{config.epochs.iterations-1}"
    trial_progress = f"trial {trial.index}/{len(trials)-1}"
    print(f"Running {epoch_progress}, {iteration_progress}, {trial_progress}")


def main():
    start = time()
    date: str = datetime.now().strftime("%Yy-%Mm-%dd_%Hh-%Mm-%Ss")

    config: SimulationConfig = load_arguments()

    for epoch in range(config.epochs.epochs):
        simulation: Simulation = Simulation(config, epoch)
        for iteration in range(config.epochs.iterations):
            print(f"iteration = {iteration}")
            simulation.prepare_iteration(iteration)
            trials: List[SimulationTrial] = simulation.iteration_generate_trials()
            for trial in trials:
                progress(config, epoch, iteration, trial, trials)

                trial_identifier = f"{epoch:04d}ep-{iteration:04d}s-{trial.index:04d}t"
                run_trial(trial, config, trial_identifier)

    print(f"Took {time() - start}s")


if __name__ == "__main__":
    main()
