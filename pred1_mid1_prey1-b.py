from simulate import *
import matplotlib.pyplot as plt

initial_populations = [50, 10, 5]
growth_rates = [0.25, -0.1, -0.3]
coefficients = [
    [0, -0.04, -0.01],
    [0.035, 0, -0.02],
    [0.035, 0.03, 0],
]

options = SimulateOptions()
options.linewidth = 1
options.include_legend = False


simulate(
    initial_populations, growth_rates, coefficients, "pred1_mid1_prey1-b.png", options
)
plt.show()
