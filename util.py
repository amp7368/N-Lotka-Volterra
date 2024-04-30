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
    def printProgressBar(iteration):
        percent = ("{0:." + str(decimals) + "f}").format(
            100 * (iteration / float(total))
        )
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + "-" * (length - filledLength)
        print(f"\r{prefix()} |{bar}| {suffix(iteration,percent)}", end=printEnd)

    # Initial Call
    printProgressBar(0)
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        printProgressBar(i + 1)
    # Print New Line on Complete
    print()


def simulation_progress_bar(euler_step, max_time, last_generation_supplier):
    iterations = int(max_time / euler_step)

    def prefix():
        surviving_species = 0
        population = last_generation_supplier()
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


def calc_color(percentage):
    red = (1, 0, 0)
    yellow = (1, 1, 0)
    green = (0, 1, 0)
    if percentage < 0:
        return interpolate(yellow, red, -percentage)
    return interpolate(yellow, green, percentage)


def interpolate(color1, color2, fraction):
    r = interpolate_channel(color1[0], color2[0], fraction)
    g = interpolate_channel(color1[1], color2[1], fraction)
    b = interpolate_channel(color1[2], color2[2], fraction)

    return (r, g, b)


def interpolate_channel(d1, d2, fraction):
    return d1 + (d2 - d1) * fraction
