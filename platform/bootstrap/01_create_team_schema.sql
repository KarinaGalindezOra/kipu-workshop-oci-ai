-- Create one non-administrative workshop schema per team.
-- Run as an approved database administrator, once for each team.
-- Example: @platform/bootstrap/01_create_team_schema.sql T01
-- The script is idempotent: it does not alter the password of an existing user.
-- Do not pass passwords as script arguments or store them in this file.

SET VERIFY OFF
SET SERVEROUTPUT ON

DEFINE team_code = '&1'
ACCEPT team_password CHAR PROMPT 'New team schema password: ' HIDE

DECLARE
    l_team_code VARCHAR2(12) := UPPER('&team_code');
    l_user_name VARCHAR2(30);
    l_exists    NUMBER;

    PROCEDURE grant_required_privileges(p_user_name IN VARCHAR2) IS
    BEGIN
        EXECUTE IMMEDIATE 'GRANT CREATE SESSION, CREATE TABLE, CREATE INDEX, CREATE PROCEDURE TO ' || p_user_name;
        EXECUTE IMMEDIATE 'ALTER USER ' || p_user_name || ' QUOTA 512M ON DATA';
    END grant_required_privileges;
BEGIN
    IF NOT REGEXP_LIKE(l_team_code, '^T[0-9]{2}$') THEN
        RAISE_APPLICATION_ERROR(-20001, 'Team code must use the form T01 through T99.');
    END IF;

    l_user_name := 'KHIPU_WS_' || l_team_code;

    SELECT COUNT(*)
      INTO l_exists
      FROM dba_users
     WHERE username = l_user_name;

    IF l_exists = 0 THEN
        EXECUTE IMMEDIATE
            'CREATE USER ' || l_user_name ||
            ' IDENTIFIED BY "' || REPLACE('&team_password', '"', '') ||
            '" DEFAULT TABLESPACE DATA TEMPORARY TABLESPACE TEMP';
        DBMS_OUTPUT.PUT_LINE('TEAM_SCHEMA_CREATED ' || l_user_name);
    ELSE
        DBMS_OUTPUT.PUT_LINE('TEAM_SCHEMA_EXISTS ' || l_user_name);
    END IF;

    grant_required_privileges(l_user_name);
    DBMS_OUTPUT.PUT_LINE('TEAM_SCHEMA_READY ' || l_user_name);
END;
/

UNDEFINE team_code
UNDEFINE team_password
