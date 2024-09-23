select value, name, description, run_id
from analysis_datapoint dp
         left join analysis_column_name cname on dp.column_id = cname.id


