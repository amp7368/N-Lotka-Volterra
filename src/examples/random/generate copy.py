from random import gauss

import matplotlib.pyplot as plt
import numpy as np

from model.simulate import SimulateOptions, simulate
from model.write_simulation import write_meta


def random_simulation(
    species_count=200,
    independence_ratio=0.1,
    coeff_mean=0.2,
    growth_scale=1,
    growth_stddev=0.01,
    coeff_prey_stddev=0.5,
    coeff_predator_stddev=0.10,
):
    """
    species_count: number of species to generate
    indepence_ratio: What percentage of connections should be removed
    coeff_mean: The strength of connections between species
    coeff_stddev: The standard deviation of coeff
    """

    # Start with power-law populations with larger populations
    # The initial populations don't matter quite as much and will stabalize
    # They should be small enough that the graph doesn't display with a huge y-value at the start and a lower y-value later
    initial_populations = []
    for survivors in range(species_count):
        initial_populations.append(10 * (survivors + species_count / 10) ** -1.5)

    # Generate semi-random growth_rates and coefficients for each species
    growth_rates = []
    coefficients = []

    # Remove connections between species
    remove_connections = np.random.binomial(
        n=1, p=independence_ratio, size=(species_count, species_count)
    )
    for y in range(1, species_count):
        for x in range(y):
            remove_connections[x][y] = remove_connections[y][x]

    for x in range(species_count):
        # Add growth rates
        half = species_count / 2
        # x^2 in both directions centered at species_count/2
        # This growth rate works really well for this network structure
        growth = (half - x) ** 2 / half**2 + 0.0000000000001
        growth = gauss(growth ** (1.0 / growth_scale), growth_stddev)
        if x >= species_count / 2:
            growth *= -1
        growth_rates.append(growth)

        # Calculate species coefficients
        spec_coeff = []
        for y in range(species_count):
            if x == y or remove_connections[x][y] == 1:
                coeff = 0
            elif x < y:
                coeff = -gauss(coeff_mean, coeff_prey_stddev)
            elif coefficients[y][x] == 0:
                coeff = 0
            else:
                prey = coefficients[y][x]
                # predator has opposite nourishment from prey being eaten
                # therefore it has an opposite sign for coeff
                sign = 1 if prey < 0 else -1
                coeff = gauss(sign * (abs(prey) * 1.1), coeff_predator_stddev)

            spec_coeff.append(coeff)

        coefficients.append(spec_coeff)

    # Write parameters
    write_meta(growth_rates, coefficients, solname)

    options = SimulateOptions()
    options.include_legend = False

    # Do simulation
    simulation = simulate(
        initial_populations,
        growth_rates,
        coefficients,
        solname,
        options,
        plot=plot,
    )

    # write_simulation(simulation, solname)
    survivors = 0
    for species in simulation[:, -1]:
        if species != 0:
            survivors += 1
    return survivors / species_count


def run_random_simulation():
    random_simulation(plt, "randomness", independence_ratio=0.00, species_count=10)
    plt.show()
