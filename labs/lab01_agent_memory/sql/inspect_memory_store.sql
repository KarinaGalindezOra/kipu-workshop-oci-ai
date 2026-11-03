-- Read-only inspection for the Lab 1 Agent Memory store.
-- Usage from SQLcl: @inspect_memory_store.sql <MEMORY_OWNER_SCHEMA> <STORE_PREFIX>
-- This script performs SELECT statements only and does not print credentials.

set pagesize 200
set linesize 180
set feedback on
set verify off

define memory_owner = '&1'
define memory_prefix = '&2'

prompt === Current application database user ===
select user as current_database_user from dual;

prompt === Memory store tables visible through dictionary metadata ===
column table_name format a42
select table_name
from all_tables
where owner = upper('&memory_owner')
  and table_name like upper('&memory_prefix') || '\_%' escape '\'
order by table_name;

prompt === Logical model columns for the memory table ===
column column_name format a36
column data_type format a24
select column_name, data_type, nullable
from all_tab_columns
where owner = upper('&memory_owner')
  and table_name = upper('&memory_prefix') || '_MEMORY'
order by column_id;

prompt === End of read-only inspection ===
