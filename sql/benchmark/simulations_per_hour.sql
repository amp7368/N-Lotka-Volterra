select count(*)                                                                simulations,
       extract(EPOCH from (max(run_date) - min(run_date))) / 3600              hours_run,
       count(*) / (extract(EPOCH from (max(run_date) - min(run_date))) / 3600) simulations_per_hour
from trial_run;


