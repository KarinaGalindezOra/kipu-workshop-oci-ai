-- Read-only inspection of the pre-created Agent Memory store.
-- Run as the temporary application user, never as ADMIN or the memory owner.
-- Arguments: 1 = memory owner schema, 2 = memory store physical prefix.

set pagesize 100
set linesize 200

prompt Connected database user
select user as current_user from dual;

prompt Agent Memory tables visible through granted runtime access
select table_name
from all_tables
where owner = upper('&1')
  and table_name like upper('&2') || '\\_%' escape '\\'
order by table_name;

prompt Columns of the primary memory table
select column_name, data_type, nullable
from all_tab_columns
where owner = upper('&1')
  and table_name = upper('&2') || '_MEMORY'
order by column_id;
