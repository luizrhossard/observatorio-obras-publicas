-- 003_create_trusted_tables.sql
-- Trusted layer: Normalized and validated data

-- Trusted obras table
CREATE TABLE IF NOT EXISTS trusted.obras (
    obra_id VARCHAR(50) PRIMARY KEY,
    nome VARCHAR(500),
    descricao TEXT,
    uf VARCHAR(2),
    municipio VARCHAR(200),
    orgao VARCHAR(300),
    orgao_id VARCHAR(50),
    funcao VARCHAR(100),
    subfuncao VARCHAR(100),
    valor_previsto DECIMAL(18, 2),
    valor_executado DECIMAL(18, 2),
    status VARCHAR(50),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    data_inicio DATE,
    data_fim_previsto DATE,
    data_conclusao DATE,
    data_atualizacao DATE,
    fonte_recursos VARCHAR(200),
    modalidade VARCHAR(100),
    regiao VARCHAR(50),
    ingestion_timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trusted_obra_uf ON trusted.obras(uf);
CREATE INDEX IF NOT EXISTS idx_trusted_obra_status ON trusted.obras(status);
CREATE INDEX IF NOT EXISTS idx_trusted_obra_orgao ON trusted.obras(orgao);
CREATE INDEX IF NOT EXISTS idx_trusted_obra_regiao ON trusted.obras(regiao);
CREATE INDEX IF NOT EXISTS idx_trusted_obra_valor_previsto ON trusted.obras(valor_previsto);
CREATE INDEX IF NOT EXISTS idx_trusted_obra_data_inicio ON trusted.obras(data_inicio);

COMMENT ON TABLE trusted.obras IS 'Normalized obras data';
COMMENT ON COLUMN trusted.obras.obra_id IS 'Unique identifier of the obra';
COMMENT ON COLUMN trusted.obras.uf IS 'Federative Unit (Brazilian state code)';
COMMENT ON COLUMN trusted.obras.regiao IS 'Brazilian region (Norte, Nordeste, Sul, etc.)';