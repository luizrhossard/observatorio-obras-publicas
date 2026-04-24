-- 001_create_schemas.sql
-- Create database schemas for data pipeline layers

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS trusted;
CREATE SCHEMA IF NOT EXISTS analytics;

COMMENT ON SCHEMA raw IS 'Staging area for raw ingested data';
COMMENT ON SCHEMA trusted IS 'Clean, normalized data layer';
COMMENT ON SCHEMA analytics IS 'Analytics layer with fact tables and dimensions';