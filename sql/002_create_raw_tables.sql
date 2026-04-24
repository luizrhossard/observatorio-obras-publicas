-- 002_create_raw_tables.sql
-- Raw layer: Store original API responses

-- Raw obras table (JSON payload storage)
CREATE TABLE IF NOT EXISTS raw.obras_raw (
    obra_id VARCHAR(50) PRIMARY KEY,
    payload JSONB NOT NULL,
    ingestion_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    source_system VARCHAR(50) DEFAULT 'obrasgov'
);

CREATE INDEX IF NOT EXISTS idx_raw_obra_timestamp 
    ON raw.obras_raw(ingestion_timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_raw_obra_source 
    ON raw.obras_raw(source_system);

COMMENT ON TABLE raw.obras_raw IS 'Raw JSON payloads from ObrasGov API';
COMMENT ON COLUMN raw.obras_raw.obra_id IS 'Unique identifier of the obra';
COMMENT ON COLUMN raw.obras_raw.payload IS 'Complete JSON response from API';
COMMENT ON COLUMN raw.obras_raw.ingestion_timestamp IS 'Timestamp of data ingestion';