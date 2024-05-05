from os import path, makedirs
import numpy as np
import json


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


def write_file(json_obj, file: str):
    with open(file, "w") as file:
        default = lambda obj: obj.__dict__
        json.dump(json_obj, file, default=default, indent=4, sort_keys=True)


def write_meta_csv(growth_rates, coefficients, nodes_file, edges_file):
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


def write_generations_csv(simulation, file: str):
    with open(file, "w") as file:
        for time in simulation:
            for point in time:
                file.write(str(point))
                file.write(",")
            file.write("\n")
