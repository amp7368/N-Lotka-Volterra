select  DENSE_RANK () OVER(ORDER BY s.run_id) AS run_index, s.run_id as run_id,  s.id species_id,s.days_survived
from species_run s
         left join trial_run run  on s.run_id = run.id
where run.parameters_id = 'bf83c8c0-2231-4eed-bc7a-39ff57cd0a3b'
order by run_id, s.species_index;

-- View all column names
select *
from analysis_column_name;
