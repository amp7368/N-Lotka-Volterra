from os import path, makedirs


def write_meta(growth_rates, coefficients, solname: str):
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


def write_simulation(simulation, solname: str):
    data_file = path.join("out", solname + "-data.csv")
    with open(data_file, "w") as file:
        for time in simulation:
            for point in time:
                file.write(str(point))
                file.write(",")
            file.write("\n")
