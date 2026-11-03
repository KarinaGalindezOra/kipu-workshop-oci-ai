-- Run once in each participant-owned KHIPU_L2_Pnnn schema in the shared ADB.
-- New schema v2 only. Do not run against a legacy table with this name.
-- Administrator must approve DDL; use a new dedicated table/schema for migration.
-- Usage: @01_create_contract_chunks.sql <approved_vector_dimension>
SET VERIFY OFF
DEFINE vector_dimension = &1
CREATE TABLE lab02_contract_chunks (
    chunk_id VARCHAR2(128) PRIMARY KEY,
    corpus_id VARCHAR2(128) NOT NULL,
    api_name VARCHAR2(64) NOT NULL,
    contract_version VARCHAR2(8) NOT NULL,
    data_classification VARCHAR2(32) NOT NULL,
    content_hash VARCHAR2(64) NOT NULL,
    embedding_model_id VARCHAR2(512) NOT NULL,
    embedding_dimension NUMBER NOT NULL,
    embedding_input_hash VARCHAR2(64) NOT NULL,
    metadata_json CLOB NOT NULL CHECK (metadata_json IS JSON),
    embedding VECTOR(&vector_dimension, FLOAT32) NOT NULL,
    loaded_at TIMESTAMP WITH TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL,
    CHECK (contract_version IN ('v1', 'v2')),
    CHECK (data_classification = 'synthetic')
);
CREATE INDEX lab02_contract_scope_ix
    ON lab02_contract_chunks (corpus_id, api_name, contract_version);
-- Exact search is intentional. No ANN index is required for nine chunks.
UNDEFINE vector_dimension
