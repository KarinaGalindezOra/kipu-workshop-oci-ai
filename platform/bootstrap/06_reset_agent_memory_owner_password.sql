-- Reset the password for an existing Lab 1 Agent Memory owner.
-- Run as an approved ADB administrator only after validating that the owner
-- exists and is OPEN. Example:
-- @platform/bootstrap/06_reset_agent_memory_owner_password.sql T01
-- The password is prompted locally, never printed, stored, or passed as an argument.

SET VERIFY OFF
SET SERVEROUTPUT ON

DEFINE team_code = '&1'
ACCEPT owner_password CHAR PROMPT 'New memory owner password: ' HIDE

DECLARE
    l_team_code  VARCHAR2(12) := UPPER('&team_code');
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
        RAISE_APPLICATION_ERROR(-20003, 'Memory owner does not exist: ' || l_owner_name);
    END IF;

    EXECUTE IMMEDIATE
        'ALTER USER ' || DBMS_ASSERT.SIMPLE_SQL_NAME(l_owner_name) ||
        ' IDENTIFIED BY "' || REPLACE('&owner_password', '"', '') || '"';
    DBMS_OUTPUT.PUT_LINE('MEMORY_OWNER_PASSWORD_RESET ' || l_owner_name);
END;
/

UNDEFINE team_code
UNDEFINE owner_password
