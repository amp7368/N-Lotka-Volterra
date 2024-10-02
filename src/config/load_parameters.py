from config.parameters.small_world.small_world_parameters import SmallWorldParameters
from config.parameters_api import ProgramParametersApi
from env.program_env import program_env


def load_arguments() -> ProgramParametersApi:
    parameters = SmallWorldParameters()

    master_seed = program_env.run.get_or_gen_master_seed()
    return ProgramParametersApi(master_seed, parameters)
