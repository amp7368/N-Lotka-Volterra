import os
from typing import Callable, Iterable

import numpy as np

from model.simulate_options import Generation, SimulationAccuracy


def progress_bar(
    iterable: Iterable,
    prefix: Callable[[], str],
    suffix: Callable[[int, float], str],
    decimals: int = 1,
    full_length: int | None = None,
    fill: str = "=",
    printEnd: str = "\r",
):
    """
    Call in a loop to create terminal progress bar
    Modified code from from https://stackoverflow.com/questions/3173320

    @params:
        iterable    - Required  : iterable object (Iterable)
        prefix      - Required  : prefix string (Str)
        suffix      - Required  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    total = float(len(iterable))

    # Progress Bar Printing Function
    def print_progress_bar(iteration):
        start = f"\r{prefix()} |"
        end = f"| {suffix(0,0)}"
        padding_length = len(start) + len(end) + 10

        bar_length = full_length if full_length else os.get_terminal_size().columns
        # Must be at least 10 char wide
        bar_length = max(10, bar_length - padding_length)

        filled_length = int(bar_length * iteration / total)
        bar = fill * filled_length + "-" * (bar_length - filled_length)
        percent = round(100 * iteration / total, decimals)

        print(f"\r{prefix()} |{bar}| {suffix(iteration,percent)}", end=printEnd)

    # Initial Call
    print_progress_bar(0)
    # Update Progress Bar
    increment = len(iterable) / 100
    for i, item in enumerate(iterable):
        yield item

        if i >= total - 3 or i % increment == 0:
            print_progress_bar(i + 1)
    # Print New Line on Complete
    print()


def simulation_progress_bar(accuracy: SimulationAccuracy, last_gen):
    euler_step = accuracy.euler_step
    max_time = accuracy.max_time
    iterations = int(max_time / euler_step)

    def prefix() -> str:
        population: Generation = last_gen()
        surviving_species = np.count_nonzero(population)
        return f"Surviving Species ({surviving_species}/{len(population)})"

    def suffix(t: int, perc: float):
        progress = int(t * euler_step)
        return f"Time steps ({progress}/{max_time}) | {perc}% Complete"

    return progress_bar(range(iterations), prefix, suffix)


def print_populations(population):
    # count how many species have survived
    surviving_species = 0

    print("Populations:")
    for species in range(len(population)):
        spec_population = population[species]
        if spec_population != 0:
            print(f"Species P_{species+1} {spec_population} (Survived)")
            surviving_species += 1
        else:
            print(f"Species P_{species+1} - (Extinct)")

    print(f"\n{surviving_species} have survived to the end of the simulation")
