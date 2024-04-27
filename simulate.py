import matplotlib.pyplot as plt
import numpy as np
import math
from os import path

euler_step = 0.002
max_time = 300
iterations = int(max_time / euler_step)


def print_populations(population):
    print("Populations:")
    for species in range(len(population)):
        spec_population = round(population[species], 100)
        print(f"Species P_{species+1} {spec_population}")
    print()


class SimulateOptions:
    include_legend: bool = True
    linewidth: int = 2


def simulate(
    initial_populations, growth_rates, coefficients, solname, options: SimulateOptions
):
    species_count = len(initial_populations)

    populations = [initial_populations]
    last_population = initial_populations

    for t in range(iterations):
        new_population_at_t = []
        for species in range(species_count):
            population_multiplier = 0
            for species_compare in range(species_count):
                if species == species_compare:
                    population_multiplier += growth_rates[species]
                else:
                    compare_population = last_population[species_compare]
                    coeff = coefficients[species][species_compare]
                    population_multiplier += coeff * compare_population

            species_population = last_population[species]
            change_in_population = (
                euler_step * species_population * population_multiplier
            )
            species_population += change_in_population
            if math.isnan(species_population):
                change_in_population = 0

            new_population_at_t.append(species_population)

        populations.append(new_population_at_t)
        last_population = new_population_at_t

        if t % 10000 == 0:
            print(f"Population at T={round(t*euler_step)}")
            print_populations(last_population)

    print_populations(last_population)

    x = np.arange(0, max_time + euler_step, euler_step)
    x = np.expand_dims(x, axis=0).T
    x = np.tile(x, (1, species_count))
    plt.plot(x, populations)

    if options.include_legend:
        legend = []
        for x in range(species_count):
            legend.append(f"P_{x+1}")
        plt.legend(legend)

    plt.setp(plt.legend().get_lines(), linewidth=4)
    plt.ylabel("Population")
    plt.xlabel("Time")
    plt.xlim(euler_step)

    filepath = path.join("out", solname + "-plot.png")
    plt.savefig(filepath, dpi=600)
    print(f"Saved plot to {filepath}")
    return populations
