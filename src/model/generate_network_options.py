from model.generate_options import NetworkStructure


class UniformNetworkStructure(NetworkStructure):
    independence_ratio = 0.1
    coeff_mean = 0.2
    growth_scale = 1
    growth_stddev = 0.01
    coeff_prey_stddev = 0.5
    coeff_predator_stddev = 0.10
