import cmath

import numba
import numpy as np
from numba import cuda, float64, int32

from model.simulation_trial import (
    Generations,
    SimulationAccuracy,
    SimulationPopulations,
    SimulationTrial,
)

NP_DTYPE = np.float64
NB_DTYPE = float64


def simulate_gpu(trial: SimulationTrial) -> Generations:
    populations: SimulationPopulations = trial.populations
    accuracy: SimulationAccuracy = trial.accuracy

    steps_in_rounded: int = accuracy.rounded_iterations()
    steps_in_precise: int = accuracy.steps_in_precise()
    timesteps = accuracy.iterations() - steps_in_precise
    return simulate_wrapper(
        populations.initial_populations,
        populations.growth_rates,
        populations.coefficients,
        steps_in_rounded,
        timesteps,
        steps_in_precise,
        accuracy.extinct_if_below,
        accuracy.euler_step,
    )


def simulate_wrapper(
    np_initial_populations,
    np_growth_rates,
    np_coefficients,
    steps_in_rounded,
    timesteps,
    steps_in_precise,
    extinct_if_below,
    euler_step,
) -> np.ndarray[2, float]:
    species_count = len(np_initial_populations)
    with cuda.stream().auto_synchronize() as stream:
        with cuda.defer_cleanup():
            growth_rates = cuda.to_device(np_growth_rates, stream=stream)
            coefficients = cuda.to_device(np_coefficients, stream=stream)

            last_generation = cuda.to_device(np_initial_populations, stream=stream)
            if steps_in_precise == 1:
                precise_generations = cuda.device_array(
                    shape=(1, 1),
                    dtype=NP_DTYPE,
                    stream=stream,
                )
            else:
                precise_generations = cuda.device_array(
                    shape=(species_count, steps_in_precise),
                    dtype=NP_DTYPE,
                    stream=stream,
                )
            generations = cuda.device_array(
                shape=(species_count, steps_in_rounded),
                dtype=NP_DTYPE,
                stream=stream,
            )
            is_inf = cuda.device_array(shape=(1), dtype=np.int32, stream=stream)

            stream.synchronize()
            gpu_init_sim[1, species_count, stream](
                last_generation, precise_generations, generations
            )
            stream.synchronize()
            gpu_simulate[1, species_count, stream](
                last_generation,
                precise_generations,
                generations,
                growth_rates,
                coefficients,
                int32(species_count),
                int32(timesteps),
                int32(steps_in_precise),
                float64(extinct_if_below),
                float64(euler_step),
                is_inf,
            )
            stream.synchronize()

            np_generations = generations.copy_to_host(stream=stream)
            np_inf = is_inf.copy_to_host(stream=stream)
            inf_timestep = np_inf[0]
            if inf_timestep != 0:
                np_generations[inf_timestep:] = -1

    return np_generations


@cuda.jit((NB_DTYPE[:], NB_DTYPE[:, :], NB_DTYPE[:, :]))
def gpu_init_sim(last_generation, precise_generations, generations):
    pos = cuda.grid(1)
    population = last_generation[pos]
    generations[pos, 0] = population
    if precise_generations.size != 1:
        precise_generations[pos, 0] = population


@cuda.jit(
    (
        NB_DTYPE[:],
        NB_DTYPE[:, :],
        NB_DTYPE[:, :],
        NB_DTYPE[:],
        NB_DTYPE[:, :],
        numba.int32,
        numba.int32,
        numba.int32,
        NB_DTYPE,
        NB_DTYPE,
        numba.int32[:],
    ),
    device=True,
)
def gpu_simulate_timestep(
    last_generation,
    precise_generations,
    generations,
    growth_rates,
    coefficients,
    species_count,
    timestep,
    steps_in_precise,
    extinct_if_below,
    euler_step,
    is_inf,
):
    species_id = cuda.grid(1)

    change_in_population = 0.0
    # dot product
    for i in range(species_count):
        change_in_population += coefficients[species_id, i] * last_generation[i]

    change_in_population += growth_rates[species_id]

    population = last_generation[species_id]
    population += euler_step * change_in_population * population

    if cmath.isnan(population) or population < extinct_if_below:
        population = 0
    elif cmath.isinf(population) or population > 1e30:
        is_inf[0] = (timestep + 1) // steps_in_precise
        population = -1
        return

    last_generation[species_id] = population

    if steps_in_precise == 1:
        generations[species_id, timestep + 1] = population
    else:
        time_in_precise = timestep % steps_in_precise
        precise_generations[species_id, time_in_precise] = population
        if time_in_precise == steps_in_precise - 1:
            mean = 0
            for i in range(steps_in_precise):
                mean += precise_generations[species_id, i]
            generation_t = (timestep + 1) // steps_in_precise
            generations[species_id, generation_t] = mean


@cuda.jit(
    (
        NB_DTYPE[:],
        NB_DTYPE[:, :],
        NB_DTYPE[:, :],
        NB_DTYPE[:],
        NB_DTYPE[:, :],
        numba.int32,
        numba.int32,
        numba.int32,
        NB_DTYPE,
        NB_DTYPE,
        numba.int32[:],
    ),
)
def gpu_simulate(
    last_generation,
    precise_generations,
    generations,
    growth_rates,
    coefficients,
    species_count,
    timesteps,
    steps_in_precise,
    extinct_if_below,
    euler_step,
    is_inf,
):
    species_id = cuda.grid(1)

    for timestep in range(timesteps):
        if last_generation[species_id] != 0:
            gpu_simulate_timestep(
                last_generation,
                precise_generations,
                generations,
                growth_rates,
                coefficients,
                species_count,
                timestep,
                steps_in_precise,
                extinct_if_below,
                euler_step,
                is_inf,
            )
        cuda.syncthreads()
        if is_inf[0] != 0:
            return
        cuda.syncthreads()
