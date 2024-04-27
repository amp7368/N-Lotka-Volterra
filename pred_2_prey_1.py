from simulate import *
import matplotlib.pyplot as plt

initial_populations = [50, 10, 5]
growth_rates = [0.25, -0.5, -0.5]
coefficients = [
    [0, -0.04, -0.04],
    [0.04, 0, -0.02],
    [0.02, 0.04, 0],
]

options = SimulateOptions()
options.linewidth = 1
options.include_legend = False

simulate(initial_populations, growth_rates, coefficients, "pred_2_prey_1.png", options)
plt.show()
