from model.simulation_options import SimulationAccuracy


def progress_bar(
    iterable, prefix, suffix, decimals=1, length=100, fill="=", printEnd="\r"
):
    """
    Call in a loop to create terminal progress bar
    Modified code from from https://stackoverflow.com/questions/3173320

    @params:
        iterable    - Required  : iterable object (Iterable)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    total = len(iterable)

    # Progress Bar Printing Function
    def print_progress_bar(iteration):
        percent = ("{0:." + str(decimals) + "f}").format(
            100 * (iteration / float(total))
        )
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + "-" * (length - filledLength)
        print(f"\r{prefix()} |{bar}| {suffix(iteration,percent)}", end=printEnd)

    # Initial Call
    print_progress_bar(0)
    # Update Progress Bar
    increment = len(iterable) / 100
    for i, item in enumerate(iterable):
        yield item

        if i + 1 == len(iterable) or i % increment == 0:
            print_progress_bar(i + 1)
    # Print New Line on Complete
    print()


def simulation_progress_bar(accuracy: SimulationAccuracy, last_gen_supplier):
    euler_step = accuracy.euler_step
    max_time = accuracy.max_time
    iterations = int(max_time / euler_step)

    def prefix():
        surviving_species = 0
        population = last_gen_supplier()
        for spec in population:
            if spec != 0:
                surviving_species += 1
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
