from simulate import *
import matplotlib.pyplot as plt

initial_populations = [50, 10, 15, 5]
growth_rates = [0.25, -0.1, -0.3, -0.1]
coefficients = [
    [0, -0.04, -0.01, -0.02],
    [0.035, 0, -0.02, -0.015],
    [0.035, 0.03, 0, -0.02],
    [0.02, 0.02, 0, 0],
]

options = SimulateOptions()
simulate(initial_populations, growth_rates, coefficients, "workshop-b.png", options)
plt.show()
