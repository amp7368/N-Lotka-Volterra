import numpy as np

from model.plot_simulation import plot_generations
from model.population_util import SimulationPopulations
from model.simulation_trial import (
    Generation,
    Generations,
    SimulationAccuracy,
    SimulationTrial,
)


def simulate(trial: SimulationTrial) -> Generations:
    err = np.geterrobj()
    np.seterr(over="ignore", under="ignore")

    populations: SimulationPopulations = trial.populations
    accuracy: SimulationAccuracy = trial.accuracy

    initial_populations: np.ndarray[float] = np.array(populations.initial_populations)
    coefficients: np.ndarray[np.ndarray[float]] = np.array(populations.coefficients)
    growth_rates: np.ndarray[float] = np.array(populations.growth_rates)

    species_count: int = len(initial_populations)

    generations: Generations = np.zeros(
        (species_count, accuracy.rounded_iterations()), dtype=np.float32
    )

    steps_in_rounded: int = accuracy.steps_in_rounded()
    precise_generation: Generations = np.zeros((species_count, steps_in_rounded))

    generations[:, 0] = initial_populations
    last_generation: Generation = initial_populations
    for t in range(0, accuracy.iterations() - steps_in_rounded):
        change_in_population: np.ndarray[float] = (
            np.squeeze(np.dot(coefficients, last_generation)) + growth_rates
        )

        change_in_population *= last_generation * accuracy.euler_step

        new_generation = last_generation + change_in_population
        is_infinity = np.logical_or(np.isinf(new_generation), new_generation > 1e30)
        if np.any(is_infinity):
            generations[:, (t + 1) // steps_in_rounded :] = -1
            break

        is_extinct = np.logical_or(
            np.isnan(new_generation),
            new_generation < accuracy.extinct_if_below,
        )
        new_generation[is_extinct] = 0

        precise_generation[:, t % steps_in_rounded] = last_generation = new_generation

        if (t + 1) % steps_in_rounded == 0:
            generation_t = (t + 1) // steps_in_rounded
            generations[:, generation_t] = precise_generation.mean(axis=1)
    np.seterrobj(err)
    print(f"survived = {np.sum(generations[:, -1] != 0)}")
    # plot_generations(generations, trial)

    return generations
