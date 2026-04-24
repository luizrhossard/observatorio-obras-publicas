-- 005_kpi_queries.sql
-- KPI queries for analytics layer

-- KPI 1: Quantidade de obras por status
SELECT 
    s.status_nome AS status,
    COUNT(o.obra_id) AS quantidade
FROM analytics.fact_obras o
JOIN analytics.dim_status s ON o.status_key = s.status_id
GROUP BY s.status_nome, s.status_id
ORDER BY quantidade DESC;

-- KPI 2: Quantidade de obras por UF
SELECT 
    l.uf AS uf,
    l.regiao AS regiao,
    COUNT(o.obra_id) AS quantidade
FROM analytics.fact_obras o
JOIN analytics.dim_localidade l ON o.uf_key = l._localidade_id
GROUP BY l.uf, l.regiao
ORDER BY quantidade DESC;

-- KPI 3: Valor previsto total por órgão
SELECT 
    o.orgao_nome AS orgao,
    SUM(f.valor_previsto) AS valor_total
FROM analytics.fact_obras f
JOIN analytics.dim_orgao o ON f.orgao_key = o.orgao_id
GROUP BY o.orgao_nome
ORDER BY valor_total DESC
LIMIT 20;

-- KPI 4: Total de obras por região
SELECT 
    l.regiao AS regiao,
    COUNT(o.obra_id) AS total_obras,
    SUM(o.valor_previsto) AS valor_total
FROM analytics.fact_obras o
JOIN analytics.dim_localidade l ON o.regiao_key = l._localidade_id
GROUP BY l.regiao
ORDER BY total_obras DESC;

-- KPI 5: Obras concluídas vs paralisadas vs em execução
SELECT 
    s.status_categoria,
    COUNT(o.obra_id) AS quantidade,
    SUM(o.valor_previsto) AS valor_total
FROM analytics.fact_obras o
JOIN analytics.dim_status s ON o.status_key = s.status_id
WHERE s.status_categoria IN ('CONCLUIDA', 'PARALISADA', 'EM_EXECUCAO')
GROUP BY s.status_categoria
ORDER BY quantidade DESC;

-- KPI 6: Evolução temporal de obras (por ano de início)
SELECT 
    t.ano AS ano,
    s.status_nome AS status,
    COUNT(o.obra_id) AS quantidade
FROM analytics.fact_obras o
JOIN analytics.dim_tempo t ON o.data_inicio_key = t.data_id
JOIN analytics.dim_status s ON o.status_key = s.status_id
GROUP BY t.ano, s.status_nome
ORDER BY ano, quantidade DESC;

-- KPI 7: Top 10 municípios com mais obras
SELECT 
    tr.municipio AS municipio,
    tr.uf AS uf,
    COUNT(*) AS quantidade_obras,
    SUM(tr.valor_previsto) AS valor_total
FROM trusted.obras tr
WHERE tr.municipio IS NOT NULL
GROUP BY tr.municipio, tr.uf
ORDER BY quantidade_obras DESC
LIMIT 10;

-- KPI 8: Taxa de execução por região
SELECT 
    l.regiao AS regiao,
    SUM(f.valor_previsto) AS valor_previsto,
    SUM(f.valor_executado) AS valor_executado,
    ROUND(
        (SUM(f.valor_executado)::NUMERIC / NULLIF(SUM(f.valor_previsto), 0)) * 100, 
        2
    ) AS taxa_execucao_percent
FROM analytics.fact_obras f
JOIN analytics.dim_localidade l ON f.uf_key = l._localidade_id
GROUP BY l.regiao
ORDER BY taxa_execucao_percent DESC;

-- View: Resumo executivo por UF
CREATE OR REPLACE VIEW analytics.v_resumo_uf AS
SELECT 
    tr.uf,
    tr.regiao,
    COUNT(*) AS total_obras,
    SUM(CASE WHEN tr.status = 'CONCLUIDA' THEN 1 ELSE 0 END) AS concluidas,
    SUM(CASE WHEN tr.status = 'EM_EXECUCAO' THEN 1 ELSE 0 END) AS em_execucao,
    SUM(CASE WHEN tr.status = 'PARALISADA' THEN 1 ELSE 0 END) AS paralisadas,
    SUM(tr.valor_previsto) AS valor_previsto_total,
    SUM(tr.valor_executado) AS valor_executado_total
FROM trusted.obras tr
GROUP BY tr.uf, tr.regiao;

-- View: Resumo por status
CREATE OR REPLACE VIEW analytics.v_resumo_status AS
SELECT 
    tr.status,
    COUNT(*) AS total_obras,
    SUM(tr.valor_previsto) AS valor_previsto_total,
    SUM(tr.valor_executado) AS valor_executado_total,
    ROUND(
        (SUM(tr.valor_executado)::NUMERIC / NULLIF(SUM(tr.valor_previsto), 0)) * 100,
        2
    ) AS taxa_execucao_percent
FROM trusted.obras tr
WHERE tr.status IS NOT NULL
GROUP BY tr.status;