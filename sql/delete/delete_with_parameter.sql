select *
from parameters;

-- (
--     '6286e76a-87f0-4477-9393-3603d513507e',
--     '3a9c51f1-6ebc-4c14-9438-cf2824711168',
--     '0fcabe6c-5d4b-4e68-82f4-d5df984439fe'
-- )

delete
from analysis_datapoint
where exists((select t.parameters_id
              from trial_run t
              where t.parameters_id in :parameter_ids
                and run_id = t.id));


select s.id
into temporary
    table temm
from species_run s
         left join trial_run t on s.run_id = t.id
where t.parameters_id in :parameter_ids;

delete
from species_run
where species_run.id in (select id from temm);

drop table temm;

delete
from trial_run
where parameters_id in :parameter_ids;

delete
from parameters
where id in :parameter_ids

select *
from parameters
