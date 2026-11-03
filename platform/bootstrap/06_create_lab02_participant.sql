-- Lab 2 only: executed by create_lab02_participant.py using bound values.
-- One new user/schema per participant in the shared workshop ADB.
-- Not a SQL*Plus substitution script; passwords never enter source substitution.
DECLARE
    l_code VARCHAR2(32) := UPPER(:participant_code);
    l_password VARCHAR2(128) := :participant_password;
    l_user VARCHAR2(30);
    l_exists NUMBER;
BEGIN
    IF NOT REGEXP_LIKE(l_code, '^P[0-9]{3}$') OR l_code = 'P000' THEN
        RAISE_APPLICATION_ERROR(-20001, 'Use participant code P001 through P999.');
    END IF;
    IF LENGTH(l_password) NOT BETWEEN 16 AND 64
        OR REGEXP_LIKE(l_password, '[^!-~]')
        OR INSTR(l_password, ' ') > 0
        OR INSTR(l_password, '"') > 0
        OR INSTR(l_password, '''') > 0 THEN
        RAISE_APPLICATION_ERROR(-20003, 'Use 16-64 printable ASCII password characters without spaces or quotes.');
    END IF;
    l_user := 'KHIPU_L2_' || l_code;
    SELECT COUNT(*) INTO l_exists FROM dba_users WHERE username = l_user;
    IF l_exists <> 0 THEN
        RAISE_APPLICATION_ERROR(-20002, 'User exists: audit before reuse.');
    END IF;
    EXECUTE IMMEDIATE 'CREATE USER ' || DBMS_ASSERT.SIMPLE_SQL_NAME(l_user) ||
        ' IDENTIFIED BY "' || l_password ||
        '" DEFAULT TABLESPACE DATA TEMPORARY TABLESPACE TEMP';
    EXECUTE IMMEDIATE 'GRANT CREATE SESSION, CREATE TABLE TO ' ||
        DBMS_ASSERT.SIMPLE_SQL_NAME(l_user);
    EXECUTE IMMEDIATE 'ALTER USER ' || DBMS_ASSERT.SIMPLE_SQL_NAME(l_user) ||
        ' QUOTA 128M ON DATA';
END;
