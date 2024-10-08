import numpy as np

from model.simulation_cpu import GENERATIONS_DTYPE
from model.simulation_trial import Generations, SimulationTrial
from store.dbase import db
from store.entity.dcoefficients import DCoefficients
from store.entity.dparameters import DParameters
from store.entity.drun import DRun
from store.entity.dspecies_run import DSpeciesRun


def save_trial(
    dparameters: DParameters, trial: SimulationTrial, generations: Generations
) -> DRun:
    survival_days = np.where(generations != -1, generations, 0)
    survival_days = np.count_nonzero(survival_days, axis=1).astype(GENERATIONS_DTYPE)
    survival_days *= trial.accuracy.euler_step

    with db.sess() as sess:
        populations = trial.populations
        coefficients = populations.coefficients
        spec_count = len(populations.initial_populations)

        sess.add(dparameters)
        drun: DRun = DRun(trial, dparameters)
        sess.add(drun)
        sess.commit()

        all_species = []
        for species_id in range(spec_count):
            initial_population = populations.initial_populations[species_id]
            growth_rate = populations.growth_rates[species_id]
            species = DSpeciesRun(
                drun,
                species_id,
                growth_rate,
                initial_population,
                survival_days[species_id],
            )
            sess.add(species)
            all_species.append(species)
        sess.commit()

        for source in range(spec_count - 1):
            for target in range(source + 1, spec_count):
                s_to_t = coefficients[source][target]
                t_to_s = coefficients[target][source]
                if t_to_s == 0 and s_to_t == 0:
                    continue

                coeff = DCoefficients(
                    all_species[source], all_species[target], s_to_t, t_to_s
                )
                sess.add(coeff)
        sess.commit()
    return drun
