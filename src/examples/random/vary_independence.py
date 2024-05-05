import numpy as np
import matplotlib.pyplot as plt

from os import path
from examples.random.random_simulation import random_simulation


def run_vary_independence():
    fig, axs = plt.subplots(5, 2)
    survivors = np.arange(10).reshape((5, 2))

    # Vary independence ratio from 0 to 100% independence
    for x in range(0, 2):
        for y in range(0, 5):
            ratio = (x * 5 + y) / 10
            print(f"({int(ratio*100)}%) Independence")
            solname = path.join("vary_independence", f"indep_{int(ratio*100)}")
            surv = random_simulation(
                axs[y, x], solname, independence_ratio=ratio, species_count=10
            )
            survivors[y, x] = int(round(surv, 2) * 100)

    print("Surviving Populations:")
    for y in range(0, 5):
        print("| ", end="")
        for x in range(0, 2):
            print(f"{survivors[y,x]}% survived | ", end="")
        print()

    plt.show()
