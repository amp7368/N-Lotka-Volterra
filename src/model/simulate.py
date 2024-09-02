import matplotlib.pyplot as plt
import numpy as np

from args.subcommand.simulate_args import SimulateNLVArgs
from model.simulate_options import (
    Generation,
    Generations,
    SimulationAccuracy,
    SimulationOptions,
    SimulationPlot,
    SimulationPopulations,
)
from model.util import simulation_progress_bar
from model.write_simulation import write_file, write_generations_csv, write_meta_csv
from util.color_util import calc_color


def simulate(options=SimulationOptions()):
    populations: SimulationPopulations = options.populations
    accuracy: SimulationAccuracy = options.accuracy

    initial_populations: np.array[float] = np.array(populations.initial_populations)
    coefficients: np.array[np.array[float]] = np.array(populations.coefficients)
    growth_rates: np.array[float] = np.array(populations.growth_rates)

    species_count: int = len(initial_populations)

    generations: Generations = np.zeros((species_count, accuracy.iterations()))
    generations[:, 0] = initial_populations
    last_generation: Generation = initial_populations

    def last_gen_supplier() -> Generation:
        return last_generation

    for t in simulation_progress_bar(accuracy, last_gen_supplier):
        change_in_population: np.array[float] = (
            np.squeeze(np.dot(coefficients, last_generation)) + growth_rates
        )

        change_in_population *= last_generation * accuracy.euler_step

        new_generation = last_generation + change_in_population
        is_extinct = np.logical_or(
            np.isnan(new_generation),
            new_generation < accuracy.extinct_if_below,
        )
        new_generation[is_extinct] = 0
        generations[:, t] = new_generation
        last_generation = new_generation

    return generations


def plot_generations(
    options: SimulationOptions,
    generations: Generations,
    interactive: bool,
    plot=plt,
    out_file=None,
):
    populations: SimulationPopulations = options.populations
    accuracy: SimulationAccuracy = options.accuracy
    plot_opts: SimulationPlot = options.plot

    initial_populations, growth_rates = (
        populations.initial_populations,
        populations.growth_rates,
    )
    species_count: int = len(initial_populations)

    ticks = accuracy.iterations()
    if plot_opts.round_to_ticks < ticks:
        ticks = plot_opts.round_to_ticks
        rounded = np.zeros((species_count, ticks))
        iter_per_tick = accuracy.iterations() / ticks
        for i in range(ticks):
            lower = int(i * iter_per_tick)
            upper = int(lower + iter_per_tick)
            rounded[:, i] = np.sum(generations[:, lower:upper], axis=1)
    else:
        rounded = generations

    x = np.arange(0, ticks) * accuracy.euler_step

    plt.figure(figsize=(plot_opts.dim_x, plot_opts.dim_y))
    fig = plot.gcf()
    for i in range(species_count):
        # Color-gradient based on the growth rates (green=positive growth rate, red=negative growth rate)
        perc_herbivore = growth_rates[i]
        if perc_herbivore < 0:
            perc_herbivore /= -min(growth_rates)
        else:
            perc_herbivore /= max(1, max(growth_rates))
        color = calc_color(perc_herbivore)

        # This commentted code kinda looks like a power law distribution?
        # alive = np.where(populations[50:, :] != 0)
        # counts, bins = np.histogram(populations[50:, :][alive], range=(0, 10))
        # plt.stairs(counts, bins)
        plot.plot(x, np.squeeze(rounded[i, :]), color=color)

    plot.setp(plot.legend([]).get_lines(), linewidth=plot_opts.linewidth)
    if plot_opts.include_legend:
        legend = []
        for x in range(species_count):
            legend.append(f"P_{x+1}")
        fig.legend(legend)
    plot.xlabel("Time")
    plot.ylabel("Population")
    plot.xlim(accuracy.euler_step)

    if interactive:
        plot.show(block=False)
    if out_file:
        fig.savefig(out_file, dpi=plot_opts.dpi)
    if interactive:
        plot.show()


def run_simulate(args: SimulateNLVArgs):
    out_config_file = args.output_file("config", "json")
    edges_file = args.output_file("edges", "csv")
    nodes_file = args.output_file("nodes", "csv")
    plot_file = args.output_file("plot", "png")
    generations_file = args.output_file("generations", "csv")

    config: SimulationOptions = args.config()
    populations: SimulationPopulations = config.populations

    write_file(config, out_config_file)
    write_meta_csv(
        populations.growth_rates, populations.coefficients, nodes_file, edges_file
    )
    generations = simulate(config)
    write_generations_csv(generations, generations_file)

    plot_generations(config, generations, args.interactive, out_file=plot_file)

    return generations
