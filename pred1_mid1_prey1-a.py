from simulate import *
import matplotlib.pyplot as plt

initial_populations = [40, 20, 15]
growth_rates = [0.6, -0.1, -0.23]
coefficients = [
    [0, -0.01, -0.01],
    [0.005, 0, -0.0075],
    [0.002, 0.003, 0],
]


simulate(initial_populations, growth_rates, coefficients, "pred1_mid1_prey1-a")
plt.show()
