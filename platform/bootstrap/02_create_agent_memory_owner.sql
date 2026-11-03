-- Create the non-administrative schema owner for one team's Lab 1 Agent Memory store.
-- Run as an approved ADB administrator after the team ADB is provisioned.
-- Example: @platform/bootstrap/02_create_agent_memory_owner.sql T01
-- The script never prints or stores the prompted password.

SET VERIFY OFF
SET SERVEROUTPUT ON

DEFINE team_code = '&1'
ACCEPT owner_password CHAR PROMPT 'New memory owner password: ' HIDE

DECLARE
    l_team_code VARCHAR2(12) := UPPER('&team_code');
    l_owner_name VARCHAR2(30);
    l_exists     NUMBER;
BEGIN
    IF NOT REGEXP_LIKE(l_team_code, '^T[0-9]{2}$') THEN
        RAISE_APPLICATION_ERROR(-20001, 'Team code must use the form T01 through T99.');
    END IF;

    l_owner_name := 'OAM_' || l_team_code || '_OWNER';

    SELECT COUNT(*)
      INTO l_exists
      FROM dba_users
     WHERE username = l_owner_name;

    IF l_exists = 0 THEN
        EXECUTE IMMEDIATE
            'CREATE USER ' || DBMS_ASSERT.SIMPLE_SQL_NAME(l_owner_name) ||
            ' IDENTIFIED BY "' || REPLACE('&owner_password', '"', '') ||
            '" DEFAULT TABLESPACE DATA TEMPORARY TABLESPACE TEMP';
        DBMS_OUTPUT.PUT_LINE('MEMORY_OWNER_CREATED ' || l_owner_name);
    ELSE
        DBMS_OUTPUT.PUT_LINE('MEMORY_OWNER_EXISTS ' || l_owner_name);
    END IF;

    -- These are the managed-schema setup privileges documented for Agent Memory on ADB.
    -- CREATE TABLE permits the owner to create indexes for its own tables; ADB does not
    -- expose CREATE INDEX as a standalone system privilege.
    -- CREATE PROPERTY GRAPH and CREATE TRIGGER are revoked by the post-bootstrap script.
    EXECUTE IMMEDIATE 'GRANT CREATE SESSION, CREATE TABLE, CREATE SEQUENCE, CREATE VIEW, ' ||
        'CREATE PROCEDURE, CREATE JOB, CREATE PROPERTY GRAPH, CREATE TRIGGER TO ' ||
        DBMS_ASSERT.SIMPLE_SQL_NAME(l_owner_name);
    EXECUTE IMMEDIATE 'ALTER USER ' || DBMS_ASSERT.SIMPLE_SQL_NAME(l_owner_name) ||
        ' QUOTA 1G ON DATA';
    DBMS_OUTPUT.PUT_LINE('MEMORY_OWNER_READY ' || l_owner_name);
END;
/

UNDEFINE team_code
UNDEFINE owner_password
