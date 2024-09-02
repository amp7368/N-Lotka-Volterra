from typing import List
from config.load_parameters import load_arguments
from config.simulation_config import SimulationConfig
from model.simulation import Simulation
from model.simulation_trial import SimulationTrial
from model.simulation_util import simulate
from util.write_simulation import write_generations_csv, write_meta_csv

from datetime import datetime
from time import time


def main():
    start = time()

    config: SimulationConfig = load_arguments()

    date = datetime.now().strftime("%Yy-%Mm-%dd_%Hh-%Mm-%Ss")
    for epoch in range(config.epochs.epochs):
        simulation: Simulation = Simulation(config, epoch)
        for iteration in range(config.epochs.iterations):
            print(f"iteration = {iteration}")
            simulation.prepare_iteration(iteration)
            trials: List[SimulationTrial] = simulation.iteration_generate_trials()
            for trial in trials:
                generations = simulate(trial)
                seed = config.master_seed.uuid
                prefix = f"out/{seed}/"
                suffix = (
                    f"_{epoch+1:04d}ep-{iteration+1:04d}s-{trial.index+1:04d}t_{date}"
                )

                file = f"{prefix}generations{suffix}"
                write_generations_csv(generations, file)

                nodes_file = f"{prefix}nodes/{seed}_{suffix}"
                edges_file = f"{prefix}edges/{seed}_{suffix}"
                write_meta_csv(
                    trial.populations.growth_rates,
                    trial.populations.coefficients,
                    nodes_file,
                    edges_file,
                )

    duration = time() - start
    print(f"Took {duration}s")


if __name__ == "__main__":
    main()
