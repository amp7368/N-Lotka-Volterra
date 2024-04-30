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
options.euler_step = 0.002
options.max_time = 100

simulate(
    initial_populations,
    growth_rates,
    coefficients,
    "pred_2_prey_1",
    options=options,
)
plt.show()
