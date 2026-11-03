-- Review-only extension template, not executed by the MVP.
-- An administrator creates a participant-specific view over approved synthetic data.
-- Grant SELECT on that view only to the query identity; no base-table access.
-- Participant scope must come from trusted session identity, not model text.
-- Approved query ID: settled_count. Bind dates; enforce <=31 days in application.
SELECT COUNT(*) AS settled_count
FROM lab02_participant_transactions_v
WHERE status = :status
  AND occurred_at >= :start_at AND occurred_at < :end_at;
-- Reject arbitrary SQL. Use call_timeout=5000 and <=100 output rows for detail queries.
