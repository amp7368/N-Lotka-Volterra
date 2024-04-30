from typing import List
import matplotlib.pyplot as plt
import numpy as np
import math
from os import path
from util import calc_color, print_populations, simulation_progress_bar


class SimulateOptions:
    include_legend: bool = True
    linewidth: int = 1
    # Hyper-parameters about time & iterations
    euler_step = 0.005
    max_time = 200
    # Otherwise speicies will be considered alive and don't really go extinct
    extinct_if_below = 0.0000000000001

    def iterations(self):
        return int(self.max_time / self.euler_step)


def simulate(
    initial_populations: List[float],
    growth_rates: List[float],
    coefficients: List[List[float]],
    solname: str,
    options=SimulateOptions(),
    plot=plt,
):
    """
    initial_populations: The initial population
    growth_rates: An array of the rate of growth
    """
    species_count = len(initial_populations)

    populations = [initial_populations]
    last_population = initial_populations

    def last_generation_supplier():
        return populations[-1]

    for t in simulation_progress_bar(
        options.euler_step, options.max_time, last_generation_supplier
    ):
        new_population_at_t = []
        for species in range(species_count):
            species_population = last_population[species]

            if species_population == 0:
                new_population_at_t.append(0)
                continue

            population_multiplier = 0
            for species_compare in range(species_count):
                if species == species_compare:
                    population_multiplier += growth_rates[species]
                else:
                    coeff = coefficients[species][species_compare]
                    if coeff != 0:
                        compare_population = last_population[species_compare]
                        population_multiplier += coeff * compare_population

            change_in_population = (
                options.euler_step * species_population * population_multiplier
            )
            species_population += change_in_population
            is_extinct = species_population < options.extinct_if_below
            if math.isnan(species_population) or is_extinct:
                species_population = 0

            new_population_at_t.append(species_population)

        populations.append(new_population_at_t)
        last_population = new_population_at_t

    print_populations(last_population)

    populations = np.array(populations)
    x = np.arange(0, options.max_time + options.euler_step, options.euler_step)

    for i in range(species_count):
        # Color-gradient based on the growth rates (green=positive growth rate, red=negative growth rate)
        perc_herbivore = growth_rates[i]
        if perc_herbivore < 0:
            perc_herbivore /= -min(growth_rates)
        else:
            perc_herbivore /= max(growth_rates)
        # perc_herbivore = (growth_rates[i] - min(growth_rates)) / growth_range
        color = calc_color(perc_herbivore)

        # This commentted code kinda looks like a power law distribution?
        # alive = np.where(populations[50:, :] != 0)
        # counts, bins = np.histogram(populations[50:, :][alive], range=(0, 10))
        # plt.stairs(counts, bins)
        plot.plot(x, populations[:, i], color=color)

    if options.include_legend:
        legend = []
        for x in range(species_count):
            legend.append(f"P_{x+1}")
        plt.legend(legend)

    plt.ylabel("Population")
    plt.xlabel("Time")
    plt.xlim(options.euler_step)
    plt.setp(plot.legend([]).get_lines(), linewidth=0)

    filepath = path.join("out", solname + "-plot.png")
    plt.savefig(filepath, dpi=400)
    print(f"Saved plot to {filepath}")
    return populations
