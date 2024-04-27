from simulate import *
import matplotlib.pyplot as plt

initial_populations = [50, 10, 5]
growth_rates = [0.25, 0.1, -0.25]
coefficients = [
    [0, 0, -0.03],
    [0, 0, -0.02],
    [0.01, 0.06, 0],
]

options = SimulateOptions()
options.linewidth = 1
options.include_legend = False


simulate(initial_populations, growth_rates, coefficients, "pred_1_prey_2.png")
plt.show()
