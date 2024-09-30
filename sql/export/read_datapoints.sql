-- export ALL datapoints along with the column name
select data.run_id as run_id, cname.name column_name, data.value
from analysis_datapoint data
         left join analysis_column_name cname on data.cname_id = cname.id
order by run_id, column_name;

-- View all column names
select *
from analysis_column_name;
