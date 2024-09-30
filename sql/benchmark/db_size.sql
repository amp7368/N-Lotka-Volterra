SELECT table_name,
       PG_SIZE_PRETTY(table_size)   AS table_size,
       PG_SIZE_PRETTY(indexes_size) AS indexes_size,
       PG_SIZE_PRETTY(total_size)   AS total_size
FROM (SELECT table_name,
             PG_TABLE_SIZE(table_name)          AS table_size,
             PG_INDEXES_SIZE(table_name)        AS indexes_size,
             PG_TOTAL_RELATION_SIZE(table_name) AS total_size
      FROM (SELECT ('"' || schemaname || '"."' || relname || '"') AS table_name
            FROM pg_stat_user_tables) AS all_tables
      ORDER BY total_size DESC) AS pretty_sizes;


SELECT l.metric
     , l.nr                                            AS bytes
     , CASE WHEN is_size THEN pg_size_pretty(nr) END   AS bytes_pretty
     , CASE WHEN is_size THEN nr / NULLIF(x.ct, 0) END AS bytes_per_row
FROM (SELECT min(tableoid)        AS tbl     -- = 'public.tbl'::regclass::oid
           , count(*)             AS ct
           , sum(length(t::text)) AS txt_len -- length in characters
      FROM public.coefficients t -- provide table name *once*
     ) x
         CROSS JOIN LATERAL (
    VALUES (true, 'core_relation_size', pg_relation_size(tbl))
         , (true, 'visibility_map', pg_relation_size(tbl, 'vm'))
         , (true, 'free_space_map', pg_relation_size(tbl, 'fsm'))
         , (true, 'table_size_incl_toast', pg_table_size(tbl))
         , (true, 'indexes_size', pg_indexes_size(tbl))
         , (true, 'total_size_incl_toast_and_indexes', pg_total_relation_size(tbl))
         , (true, 'live_rows_in_text_representation', txt_len)
         , (false, '------------------------------', NULL)
         , (false, 'row_count', ct)
         , (false, 'live_tuples', pg_stat_get_live_tuples(tbl))
         , (false, 'dead_tuples', pg_stat_get_dead_tuples(tbl))
    ) l(is_size, metric, nr);;



select pg_size_pretty(sum(pg_column_size(target_id))),
       pg_size_pretty(sum(pg_column_size(source_id))),
       pg_size_pretty(sum(pg_column_size(target_to_source))),
       pg_size_pretty(sum(pg_column_size(source_to_target)))
from coefficients;
