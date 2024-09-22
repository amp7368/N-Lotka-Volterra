from os import makedirs, path

import numpy as np

from model.simulation_trial import Generations


def write_meta(growth_rates, coefficients, solname: str):
    nodes_file = path.join("out", solname + "-nodes.csv")
    edges_file = path.join("out", solname + "-edges.csv")
    write_meta_csv(growth_rates, coefficients, nodes_file, edges_file)
    write_meta_human(growth_rates, coefficients, solname)


def write_meta_human(growth_rates, coefficients, solname: str):
    meta_file = path.join("out", solname + "-meta.txt")
    if not path.isdir(path.dirname(meta_file)):
        makedirs(path.dirname(meta_file))
    with open(meta_file, "w") as file:
        for s1 in range(len(growth_rates)):
            growth = f"G_{s1+1} "
            file.write(f"{growth:<8}")
        file.write("\n")
        for growth in growth_rates:
            rounded = f"{round(growth, 4)} "
            file.write(f"{rounded:<8}")

        file.write("\n\nCoeff     ")
        for s1 in range(len(coefficients)):
            label = f"P_{s1+1} "
            file.write(f"{label:<10}")
        file.write("\n")
        for i in range(len(coefficients)):
            label = f"P_{i+1} "
            file.write(f"{label:<10}")

            s_coeff = coefficients[i]
            for c in s_coeff:
                val = f"{round(c,6)} "
                file.write(f"{val:<10}")
            file.write("\n")


def write_meta_csv(growth_rates, coefficients, nodes_file, edges_file):
    parent = path.dirname(edges_file)
    if not path.exists(parent):
        makedirs(parent)
    parent = path.dirname(nodes_file)
    if not path.exists(parent):
        makedirs(parent)
    with open(nodes_file, "w") as file:
        file.write("id,label,growth,herbivore\n")
        for id, growth in enumerate(growth_rates):
            herbivore = growth > 0
            label = f"h_{id}" if herbivore else f"c_{id}"
            file.write(f"{id},{label},{abs(growth)},{herbivore}\n")

    with open(edges_file, "w") as file:
        write_edges_csv(np.array(coefficients), file)


def write_edges_csv(coefficients, file):
    spec_count = len(coefficients)

    file.write("source,target,weight,prey,pred,relation,type\n")
    for source in range(spec_count):
        for target in range(source, spec_count):
            prey = coefficients[target][source]
            pred = coefficients[source][target]
            if prey == 0 and pred == 0:
                continue

            weight = abs(prey) + abs(pred)
            s, t = (source, target)
            if prey < 0 and pred >= 0:
                relation = "predator"
                directed = "directed"
            elif pred < 0 and prey >= 0:
                relation = "predator"
                directed = "directed"
                s, t = (target, source)
                prey, pred = (pred, prey)
            else:
                relation = "both"
                directed = "undirected"
            file.write(f"{s},{t},{weight},{prey},{pred},{relation},{directed}\n")


def write_generations(simulation: Generations, filename: str):
    parent = path.dirname(filename)
    if not path.exists(parent):
        makedirs(parent)

    with open(filename, "wb") as file:
        last_alive: np.ndarray[int] = np.count_nonzero(simulation, axis=1)
        species_count = len(last_alive)

        file.write(last_alive.tobytes())
        for sp in range(species_count):
            file.write(simulation[sp, :].tobytes())


def write_readable_generations_csv(simulation: Generations, filename: str):
    parent = path.dirname(filename)
    if not path.exists(parent):
        makedirs(parent)

    with open(filename, "wb") as file:
        sp = [str(i) for i in range(len(simulation[0]))]
        row = ",".join(sp)
        file.write(row + "\n")

        for time in simulation:
            for point in time:
                file.write(str(point))
            row = ",".join([str(point) for point in time])
            file.write(row + "\n")
