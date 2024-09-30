select *
from parameters
where id = :parameters_id;

-- Count the number of trial_runs completed for each parameters configurations
select count(t.id), p.id, p.start_date
from trial_run t
         left join parameters p on t.parameters_id = p.id
group by parameters_id, p.id, p.start_date
order by count(t.id) desc;
