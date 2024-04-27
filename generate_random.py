import math
from random import random, randint, gauss
from simulate import *
from write_simulation import *
import matplotlib.pyplot as plt

# number of species to generate
species_count = 50
# What percentage of the species are independent
independence_ratio = 0.8
initial_populations = []

for i in range(species_count):
    initial_populations.append(50 / (i**2 + 1))

growth_rates = []
coefficients = []
for x in range(species_count):
    growth = abs(gauss(species_count / (abs(species_count - x) ** 2 + 2), 0.5))
    if x >= species_count / 2:
        growth *= -1
    growth_rates.append(growth)
    spec_coeff = []
    for y in range(species_count):
        if x == y:
            coeff = 0
        elif x < y:
            coeff = -abs(gauss(0.2, 0.1))
        elif coefficients[y][x] == 0:
            coeff = 0
        else:
            prey = coefficients[y][x]
            coeff = gauss(math.pow(abs(prey), 1.2), 0.01)

        spec_coeff.append(coeff)

    independence = int(independence_ratio * (species_count - x))
    if independence == 0:
        coefficients.append(spec_coeff)
        continue

    for i in range(independence):
        chosen = randint(x, species_count - 1)
        spec_coeff[chosen] = 0

    coefficients.append(spec_coeff)


solname = "randomness"
write_meta(growth_rates, coefficients, solname)

options = SimulateOptions()
options.linewidth = 1
options.include_legend = False

simulation = simulate(initial_populations, growth_rates, coefficients, solname, options)
write_simulation(simulation, solname)
plt.show()
