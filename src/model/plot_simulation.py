import numpy as np
from matplotlib import pyplot as plt

from model.simulation_trial import (
    Generations,
    SimulationAccuracy,
    SimulationPopulations,
    SimulationTrial,
)
from util.color_util import calc_color


def plot_generations(generations: Generations, trial: SimulationTrial):
    populations: SimulationPopulations = trial.populations
    accuracy: SimulationAccuracy = trial.accuracy

    initial_populations, growth_rates = (
        populations.initial_populations,
        populations.growth_rates,
    )
    species_count: int = len(initial_populations)

    ticks = accuracy.rounded_iterations()
    # if plot_opts.round_to_ticks < ticks:
    #     ticks = plot_opts.round_to_ticks
    #     rounded = np.zeros((species_count, ticks))
    #     iter_per_tick = accuracy.iterations() / ticks
    #     for i in range(ticks):
    #         lower = int(i * iter_per_tick)
    #         upper = int(lower + iter_per_tick)
    #         rounded[:, i] = np.mean(generations[:, lower:upper], axis=1)
    rounded = generations

    x = np.arange(0, ticks) * accuracy.rounded_euler_step

    fig = plt.gcf()
    for i in range(species_count):
        # Color-gradient based on the growth rates (green=positive growth rate, red=negative growth rate)
        perc_herbivore = growth_rates[i]
        if perc_herbivore < 0:
            perc_herbivore /= -min(growth_rates)
        else:
            perc_herbivore /= max(growth_rates)
        color = calc_color(perc_herbivore)

        # This commentted code kinda looks like a power law distribution?
        # alive = np.where(populations[50:, :] != 0)
        # counts, bins = np.histogram(populations[50:, :][alive], range=(0, 10))
        # plt.stairs(counts, bins)
        plt.plot(x, np.squeeze(rounded[i, :]), color=color)

    plt.setp(plt.legend([]).get_lines(), linewidth=1)
    # legend = []
    # for x in range(species_count):
    #     legend.append(f"P_{x+1}")
    # fig.legend(legend)
    plt.xlabel("Time")
    plt.ylabel("Population")
    plt.ylim(-1, 200)
    plt.xlim(-1, accuracy.max_time)

    plt.show()
