-- Remove one-time Agent Memory schema-setup privileges after a successful bootstrap.
-- Run as an approved ADB administrator, never as the schema owner.
-- Example: @platform/bootstrap/05_revoke_agent_memory_setup_privileges.sql OAM_T01_OWNER

SET VERIFY OFF
SET SERVEROUTPUT ON

DEFINE owner_user = '&1'

DECLARE
    l_owner_user VARCHAR2(30) := UPPER('&owner_user');
BEGIN
    IF NOT REGEXP_LIKE(l_owner_user, '^OAM_T[0-9]{2}_OWNER$') THEN
        RAISE_APPLICATION_ERROR(-20001, 'Owner must use the form OAM_T01_OWNER.');
    END IF;

    EXECUTE IMMEDIATE 'REVOKE CREATE PROPERTY GRAPH FROM ' ||
        DBMS_ASSERT.SIMPLE_SQL_NAME(l_owner_user);
    EXECUTE IMMEDIATE 'REVOKE CREATE TRIGGER FROM ' ||
        DBMS_ASSERT.SIMPLE_SQL_NAME(l_owner_user);
    DBMS_OUTPUT.PUT_LINE('AGENT_MEMORY_SETUP_PRIVILEGES_REVOKED ' || l_owner_user);
END;
/

UNDEFINE owner_user
