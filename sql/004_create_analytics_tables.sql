-- 004_create_analytics_tables.sql
-- Analytics layer: Dimensions and fact tables

-- Dimension: Órgão (Government Agency)
CREATE TABLE IF NOT EXISTS analytics.dim_orgao (
    orgao_id SERIAL PRIMARY KEY,
    orgao_nome VARCHAR(300) NOT NULL UNIQUE,
    orgao_id_origem VARCHAR(50),
    data_carga TIMESTAMP DEFAULT NOW()
);

-- Dimension: Localidade (UF/Região)
CREATE TABLE IF NOT EXISTS analytics.dim_localidade (
    locality_id SERIAL PRIMARY KEY,
    uf VARCHAR(2) NOT NULL UNIQUE,
    regiao VARCHAR(50) NOT NULL,
    nome_regiao VARCHAR(50),
    data_carga TIMESTAMP DEFAULT NOW()
);

-- Dimension: Status da Obra
CREATE TABLE IF NOT EXISTS analytics.dim_status (
    status_id SERIAL PRIMARY KEY,
    status_nome VARCHAR(50) NOT NULL UNIQUE,
    status_descricao VARCHAR(200),
    status_categoria VARCHAR(20),
    data_carga TIMESTAMP DEFAULT NOW()
);

-- Dimension: Tempo (Data)
CREATE TABLE IF NOT EXISTS analytics.dim_tempo (
    data_id SERIAL PRIMARY KEY,
    data DATE NOT NULL UNIQUE,
    ano INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    dia INTEGER NOT NULL,
    trimestre INTEGER NOT NULL,
    nome_mes VARCHAR(20),
    nome_dia_semana VARCHAR(20),
    data_carga TIMESTAMP DEFAULT NOW()
);

-- Fact: Obras
CREATE TABLE IF NOT EXISTS analytics.fact_obras (
    obra_id SERIAL PRIMARY KEY,
    orgao_key INTEGER REFERENCES analytics.dim_orgao(orgao_id),
    uf_key INTEGER REFERENCES analytics.dim_localidade(locality_id),
    regiao_key INTEGER REFERENCES analytics.dim_localidade(locality_id),
    status_key INTEGER REFERENCES analytics.dim_status(status_id),
    data_inicio_key INTEGER REFERENCES analytics.dim_tempo(data_id),
    data_conclusao_key INTEGER REFERENCES analytics.dim_tempo(data_id),
    valor_previsto DECIMAL(18, 2),
    valor_executado DECIMAL(18, 2),
    obra_id_origem VARCHAR(50) NOT NULL UNIQUE,
    data_carga TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_fact_obras_orgao ON analytics.fact_obras(orgao_key);
CREATE INDEX IF NOT EXISTS idx_fact_obras_uf ON analytics.fact_obras(uf_key);
CREATE INDEX IF NOT EXISTS idx_fact_obras_regiao ON analytics.fact_obras(regiao_key);
CREATE INDEX IF NOT EXISTS idx_fact_obras_status ON analytics.fact_obras(status_key);

COMMENT ON TABLE analytics.fact_obras IS 'Fact table for obras analysis';
COMMENT ON COLUMN analytics.fact_obras.obra_id_origem IS 'Original obra ID from source system';