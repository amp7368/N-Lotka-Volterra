-- export ALL datapoints along with the column name
select data.run_id as run_id,
       cname.name     column_name,
       data.value
from analysis_datapoint data
         left join trial_run run on run.id = data.run_id
         left join analysis_column_name cname on data.cname_id = cname.id
-- where run.parameters_id = 'bf83c8c0-2231-4eed-bc7a-39ff57cd0a3b'
order by run_id, column_name;

-- View all column names
select *
from analysis_column_name;
