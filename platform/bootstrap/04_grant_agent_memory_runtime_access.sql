-- Grant a participant application user access to an already bootstrapped Agent Memory store.
-- Run as the team memory owner, never as the participant application user.
-- Example: @platform/bootstrap/04_grant_agent_memory_runtime_access.sql OAM_T01_P01 OAMT01
-- This script performs no CREATE, DROP, ALTER, or data-write operation.

SET VERIFY OFF
SET SERVEROUTPUT ON

DEFINE application_user = '&1'
DEFINE memory_store_id = '&2'

DECLARE
    l_application_user VARCHAR2(30) := UPPER('&application_user');
    l_memory_store_id  VARCHAR2(16) := UPPER('&memory_store_id');
    l_prefix           VARCHAR2(17);
    l_table_count      PLS_INTEGER := 0;

    PROCEDURE grant_object(p_statement IN VARCHAR2) IS
    BEGIN
        EXECUTE IMMEDIATE p_statement;
    END grant_object;
BEGIN
    IF NOT REGEXP_LIKE(l_application_user, '^OAM_T[0-9]{2}_P[0-9]{2}$') THEN
        RAISE_APPLICATION_ERROR(-20001, 'Application user must use the form OAM_T01_P01.');
    END IF;
    IF NOT REGEXP_LIKE(l_memory_store_id, '^[A-Z][A-Z0-9_]{0,15}$') THEN
        RAISE_APPLICATION_ERROR(-20002, 'Memory store ID must start with a letter and use letters, digits, or underscores only.');
    END IF;

    l_prefix := l_memory_store_id || '_';
    -- Agent Memory SDK releases can add managed tables. Grant runtime DML only
    -- on the tables belonging to this store; do not grant any CREATE privilege.
    FOR table_record IN (
        SELECT table_name
        FROM user_tables
        -- Do not use LIKE here: an underscore in a memory-store identifier is
        -- a SQL wildcard unless it is escaped. A literal prefix check ensures
        -- every SDK-managed table, including schema metadata, is granted.
        WHERE SUBSTR(table_name, 1, LENGTH(l_prefix)) = l_prefix
    ) LOOP
        grant_object('GRANT SELECT, INSERT, UPDATE, DELETE ON ' ||
            DBMS_ASSERT.SIMPLE_SQL_NAME(table_record.table_name) ||
            ' TO ' || DBMS_ASSERT.SIMPLE_SQL_NAME(l_application_user));
        l_table_count := l_table_count + 1;
    END LOOP;
    -- The cross-schema SDK startup validates the installed owner package through
    -- DBMS_AGENT_MEMORY_STORE.GET_PACKAGE_INFO(). The application user needs
    -- EXECUTE on this public runtime package, but never on its internal package.
    grant_object('GRANT EXECUTE ON DBMS_AGENT_MEMORY_STORE TO ' ||
        DBMS_ASSERT.SIMPLE_SQL_NAME(l_application_user));
    -- The registry is shared by the SDK and is not prefixed by memory_store_id.
    -- A REQUIRE_EXISTING application runtime needs this read-only registry access
    -- to validate the owner-managed store. It receives no administration privilege.
    grant_object('GRANT SELECT ON AGENT_MEMORY_STORES TO ' ||
        DBMS_ASSERT.SIMPLE_SQL_NAME(l_application_user));
    grant_object('GRANT SELECT ON PROPERTY GRAPH ' || DBMS_ASSERT.SIMPLE_SQL_NAME(l_prefix || 'MEMORY_GRAPH') ||
        ' TO ' || DBMS_ASSERT.SIMPLE_SQL_NAME(l_application_user));

    DBMS_OUTPUT.PUT_LINE('AGENT_MEMORY_RUNTIME_ACCESS_READY ' || l_application_user ||
        ' TABLES=' || l_table_count);
END;
/

UNDEFINE application_user
UNDEFINE memory_store_id
