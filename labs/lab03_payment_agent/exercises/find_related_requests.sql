-- Participant exercise: complete the fixed query; never accept a schema or SQL from the prompt.
-- Prerequisites: assigned schema, GET_PAYMENT and WS3_TRACE already deployed.
CREATE OR REPLACE FUNCTION FIND_RELATED_REQUESTS(p_payment_id VARCHAR2)
RETURN CLOB AUTHID CURRENT_USER IS
  l_payload CLOB;
BEGIN
  -- TODO: build {"requests":[{"request_id":...,"idempotency_key":...,"payload_hash":...}]}
  -- Read only WS3_REQUESTS and filter payment_id=p_payment_id using static SQL.
  -- Order by request_id. Return [] when there are no matching requests.
  RAISE_APPLICATION_ERROR(-20010,'Complete the participant exercise before running the agent');
  RETURN WS3_TRACE('find_related_requests',p_payment_id,l_payload);
END;
/
