-- Create one least-privilege Lab 1 application user for a participant.
-- Run as an approved ADB administrator after the memory owner exists.
-- Example: @platform/bootstrap/03_create_agent_memory_application_user.sql T01 P01
-- Object grants are deliberately applied only after the owner bootstraps the memory store.

SET VERIFY OFF
SET SERVEROUTPUT ON

DEFINE team_code = '&1'
DEFINE participant_code = '&2'
ACCEPT application_password CHAR PROMPT 'New application user password: ' HIDE

DECLARE
    l_team_code        VARCHAR2(12) := UPPER('&team_code');
    l_participant_code VARCHAR2(12) := UPPER('&participant_code');
    l_user_name        VARCHAR2(30);
    l_exists           NUMBER;
BEGIN
    IF NOT REGEXP_LIKE(l_team_code, '^T[0-9]{2}$') THEN
        RAISE_APPLICATION_ERROR(-20001, 'Team code must use the form T01 through T99.');
    END IF;
    IF NOT REGEXP_LIKE(l_participant_code, '^P[0-9]{2}$') THEN
        RAISE_APPLICATION_ERROR(-20002, 'Participant code must use the form P01 through P99.');
    END IF;

    l_user_name := 'OAM_' || l_team_code || '_' || l_participant_code;

    SELECT COUNT(*)
      INTO l_exists
      FROM dba_users
     WHERE username = l_user_name;

    IF l_exists = 0 THEN
        EXECUTE IMMEDIATE
            'CREATE USER ' || DBMS_ASSERT.SIMPLE_SQL_NAME(l_user_name) ||
            ' IDENTIFIED BY "' || REPLACE('&application_password', '"', '') ||
            '" DEFAULT TABLESPACE DATA TEMPORARY TABLESPACE TEMP';
        DBMS_OUTPUT.PUT_LINE('APPLICATION_USER_CREATED ' || l_user_name);
    ELSE
        DBMS_OUTPUT.PUT_LINE('APPLICATION_USER_EXISTS ' || l_user_name);
    END IF;

    EXECUTE IMMEDIATE 'GRANT CREATE SESSION TO ' || DBMS_ASSERT.SIMPLE_SQL_NAME(l_user_name);
    DBMS_OUTPUT.PUT_LINE('APPLICATION_USER_READY ' || l_user_name);
END;
/

UNDEFINE team_code
UNDEFINE participant_code
UNDEFINE application_password
