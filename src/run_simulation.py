from concurrent.futures import ThreadPoolExecutor
from time import time
from typing import Callable, List

from analyze.analyze import analyze_trial
from config.parameters_api import ProgramParametersApi
from model.simulation import SimulationSeries
from model.simulation_trial import Generations, SimulationTrial
from store.entity.dparameters import DParameters
from store.save.save_trial import save_trial
from util.write_simulation import write_generations, write_meta_csv


def choose_simulate_fn() -> Callable[[SimulationTrial], Generations]:
    import numba.cuda

    global simulate
    if numba.cuda.is_available():
        from model.simulation_gpu import simulate_gpu

        device = numba.cuda.get_current_device()
        compute_v = "v" + ".".join(map(str, device.compute_capability))
        print(f"Running program on device {device} with CUDA-Compute={compute_v}")
        return simulate_gpu
    else:
        from model.simulation_cpu import simulate_cpu

        print("Running in CPU! Performance will be impacted!")
        return simulate_cpu


simulate = choose_simulate_fn()

SHOULD_WRITE_SIMULATIONS: bool = False


executor = ThreadPoolExecutor(max_workers=2)


def run(
    trial: SimulationTrial,
    dparameters: DParameters,
    generations: Generations,
):
    drun = save_trial(dparameters, trial)
    analyze_trial(dparameters, drun, trial, generations)


def run_trial(
    trial: SimulationTrial,
    dparameters: DParameters,
    config: ProgramParametersApi,
    trial_identifier: str,
):
    generations: Generations = simulate(trial)

    executor.submit(run, trial, dparameters, generations)

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


def progress(config, epoch, iteration, trial, trials, duration):
    epoch_progress = f"epoch {epoch}/{config.epochs.epochs-1}"
    iteration_progress = f"iter {iteration}/{config.epochs.iterations-1}"
    trial_progress = f"trial {trial.index}/{len(trials)-1}"
    print(
        f"Took {round(duration,3)} to run {epoch_progress}, {iteration_progress}, {trial_progress}"
    )


def run_simulation(config, dparameters, series_id):
    simulation: SimulationSeries = SimulationSeries(config, series_id)
    trials: List[SimulationTrial] = simulation.iteration_generate_trials()
    for trial in trials:
        trial_identifier = (
            f"{series_id.epoch:04d}ep-{series_id.iteration:04d}s-{trial.index:04d}t"
        )
        start = time()
        run_trial(trial, dparameters, config, trial_identifier)
        duration = time() - start
        progress(config, series_id.epoch, series_id.iteration, trial, trials, duration)
