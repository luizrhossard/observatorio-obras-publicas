-- 007_metabase_dashboard_views.sql
-- Views otimizadas para dashboard no Metabase
-- Referência: Dashboard de Obras Públicas (PDF)

-- =====================================================
-- KPIs GERAIS (Cards de topo do dashboard)
-- =====================================================

-- View: Total de obras
CREATE OR REPLACE VIEW analytics.v_metabase_total_obras AS
SELECT
    COUNT(*) AS total_obras
FROM analytics.fact_obras;

-- View: Valor total das obras
CREATE OR REPLACE VIEW analytics.v_metabase_valor_total AS
SELECT
    COALESCE(SUM(valor_previsto), 0) AS valor_total_previsto,
    COALESCE(SUM(valor_executado), 0) AS valor_total_executado
FROM analytics.fact_obras;

-- View: Resumo de indicadores gerais
CREATE OR REPLACE VIEW analytics.v_metabase_kpi_geral AS
SELECT
    COUNT(*) AS total_obras,
    COALESCE(SUM(f.valor_previsto), 0) AS valor_total_previsto,
    COALESCE(SUM(f.valor_executado), 0) AS valor_total_executado,
    COUNT(DISTINCT o.orgao_nome) AS total_orgaos,
    COUNT(DISTINCT l.uf) AS total_ufs
FROM analytics.fact_obras f
LEFT JOIN analytics.dim_orgao o ON f.orgao_key = o.orgao_id
LEFT JOIN analytics.dim_localidade l ON f.uf_key = l.locality_id;

-- =====================================================
-- GRÁFICO 1: Pizza - Obras por Situação
-- =====================================================

CREATE OR REPLACE VIEW analytics.v_metabase_obras_por_situacao AS
SELECT
    s.status_nome AS situacao,
    s.status_categoria,
    COUNT(o.obra_id) AS quantidade,
    ROUND(
        (COUNT(o.obra_id)::NUMERIC / SUM(COUNT(o.obra_id)) OVER()) * 100,
        2
    ) AS percentual
FROM analytics.fact_obras o
JOIN analytics.dim_status s ON o.status_key = s.status_id
GROUP BY s.status_nome, s.status_categoria
ORDER BY quantidade DESC;

-- =====================================================
-- GRÁFICO 2: Barras - Obras por Região
-- =====================================================

CREATE OR REPLACE VIEW analytics.v_metabase_obras_por_regiao AS
SELECT
    l.regiao,
    l.uf,
    COUNT(o.obra_id) AS quantidade_obras,
    COALESCE(SUM(o.valor_previsto), 0) AS valor_total,
    ROUND(
        (COUNT(o.obra_id)::NUMERIC / SUM(COUNT(o.obra_id)) OVER()) * 100,
        2
    ) AS percentual
FROM analytics.fact_obras o
JOIN analytics.dim_localidade l ON o.uf_key = l.locality_id
GROUP BY l.regiao, l.uf
ORDER BY quantidade_obras DESC;

-- =====================================================
-- GRÁFICO 3: Linha - Evolução de obras por mês
-- =====================================================

CREATE OR REPLACE VIEW analytics.v_metabase_evolucao_mensal AS
SELECT
    t.ano,
    t.mes,
    t.nome_mes,
    s.status_nome AS situacao,
    COUNT(o.obra_id) AS quantidade_obras,
    COALESCE(SUM(o.valor_previsto), 0) AS valor_total
FROM analytics.fact_obras o
JOIN analytics.dim_tempo t ON o.data_inicio_key = t.data_id
JOIN analytics.dim_status s ON o.status_key = s.status_id
GROUP BY t.ano, t.mes, t.nome_mes, s.status_nome
ORDER BY t.ano, t.mes;

-- Evolução acumulada (útil para gráfico de linha acumulada)
CREATE OR REPLACE VIEW analytics.v_metabase_evolucao_acumulada AS
SELECT
    ano,
    mes,
    nome_mes,
    situacao,
    quantidade_obras,
    SUM(quantidade_obras) OVER (
        PARTITION BY situacao
        ORDER BY ano, mes
        ROWS UNBOUNDED PRECEDING
    ) AS quantidade_acumulada
FROM analytics.v_metabase_evolucao_mensal;

-- =====================================================
-- GRÁFICO 4: Barras horizontais - Top 10 órgãos com mais obras
-- =====================================================

CREATE OR REPLACE VIEW analytics.v_metabase_top_orgaos AS
SELECT
    o.orgao_nome,
    COUNT(f.obra_id) AS quantidade_obras,
    COALESCE(SUM(f.valor_previsto), 0) AS valor_total,
    ROW_NUMBER() OVER (ORDER BY COUNT(f.obra_id) DESC) AS ranking
FROM analytics.fact_obras f
JOIN analytics.dim_orgao o ON f.orgao_key = o.orgao_id
GROUP BY o.orgao_nome
ORDER BY quantidade_obras DESC
LIMIT 10;

-- =====================================================
-- TABELA: Lista detalhada de obras
-- =====================================================

CREATE OR REPLACE VIEW analytics.v_metabase_lista_obras AS
SELECT
    o.obra_id,
    o.obra_id_origem,
    org.orgao_nome AS orgao,
    s.status_nome AS situacao,
    s.status_categoria,
    l.regiao,
    l.uf,
    t.data AS data_inicio,
    t.ano AS ano_inicio,
    o.valor_previsto,
    o.valor_executado,
    CASE
        WHEN o.valor_previsto > 0 THEN
            ROUND((o.valor_executado / o.valor_previsto) * 100, 2)
        ELSE 0
    END AS percentual_execucao
FROM analytics.fact_obras o
JOIN analytics.dim_orgao org ON o.orgao_key = org.orgao_id
JOIN analytics.dim_status s ON o.status_key = s.status_id
JOIN analytics.dim_localidade l ON o.uf_key = l.locality_id
LEFT JOIN analytics.dim_tempo t ON o.data_inicio_key = t.data_id
ORDER BY o.data_carga DESC;

-- =====================================================
-- FILTROS PARA DASHBOARD
-- =====================================================

-- View: Lista única de situações para filtro
CREATE OR REPLACE VIEW analytics.v_metabase_filtro_situacao AS
SELECT DISTINCT
    s.status_nome,
    s.status_categoria,
    COUNT(o.obra_id) AS quantidade
FROM analytics.fact_obras o
JOIN analytics.dim_status s ON o.status_key = s.status_id
GROUP BY s.status_nome, s.status_categoria
ORDER BY status_nome;

-- View: Lista única de regiões para filtro
CREATE OR REPLACE VIEW analytics.v_metabase_filtro_regiao AS
SELECT DISTINCT
    l.regiao,
    l.uf,
    COUNT(o.obra_id) AS quantidade
FROM analytics.fact_obras o
JOIN analytics.dim_localidade l ON o.uf_key = l.locality_id
GROUP BY l.regiao, l.uf
ORDER BY regiao, uf;

-- View: Lista única de anos para filtro
CREATE OR REPLACE VIEW analytics.v_metabase_filtro_ano AS
SELECT DISTINCT
    t.ano,
    COUNT(o.obra_id) AS quantidade
FROM analytics.fact_obras o
JOIN analytics.dim_tempo t ON o.data_inicio_key = t.data_id
WHERE t.ano IS NOT NULL
GROUP BY t.ano
ORDER BY t.ano DESC;

-- =====================================================
-- VIEW CONSOLIDADA PARA DASHBOARD COMPLETO
-- =====================================================

CREATE OR REPLACE VIEW analytics.v_metabase_dashboard_completo AS
SELECT
    -- Identificação
    o.obra_id,
    o.obra_id_origem,

    -- Dimensões
    org.orgao_nome AS orgao,
    s.status_nome AS situacao,
    s.status_categoria,
    l.regiao,
    l.uf,

    -- Tempo
    t.ano AS ano_inicio,
    t.trimestre,
    t.nome_mes AS mes_inicio,

    -- Valores
    o.valor_previsto,
    o.valor_executado,

    -- Indicadores calculados
    CASE
        WHEN o.valor_previsto > 0 THEN
            ROUND((o.valor_executado / o.valor_previsto) * 100, 2)
        ELSE 0
    END AS percentual_execucao,

    CASE
        WHEN s.status_categoria = 'CONCLUIDA' THEN 1
        ELSE 0
    END AS is_concluida,

    CASE
        WHEN s.status_categoria = 'PARALISADA' THEN 1
        ELSE 0
    END AS is_paralisada,

    CASE
        WHEN s.status_categoria = 'EM_EXECUCAO' THEN 1
        ELSE 0
    END AS is_em_execucao

FROM analytics.fact_obras o
JOIN analytics.dim_orgao org ON o.orgao_key = org.orgao_id
JOIN analytics.dim_status s ON o.status_key = s.status_id
JOIN analytics.dim_localidade l ON o.uf_key = l.locality_id
LEFT JOIN analytics.dim_tempo t ON o.data_inicio_key = t.data_id;

-- =====================================================
-- COMENTÁRIOS PARA DOCUMENTAÇÃO NO METABASE
-- =====================================================

COMMENT ON VIEW analytics.v_metabase_kpi_geral IS 'KPIs gerais para cards do dashboard: total de obras, valores totais, quantidade de órgãos e UFs';
COMMENT ON VIEW analytics.v_metabase_obras_por_situacao IS 'Distribuição de obras por situação (pizza/rosca)';
COMMENT ON VIEW analytics.v_metabase_obras_por_regiao IS 'Distribuição de obras por região/UF (barras)';
COMMENT ON VIEW analytics.v_metabase_evolucao_mensal IS 'Evolução temporal de obras por mês (linha)';
COMMENT ON VIEW analytics.v_metabase_top_orgaos IS 'Top 10 órgãos com mais obras (barras horizontais)';
COMMENT ON VIEW analytics.v_metabase_lista_obras IS 'Lista detalhada de todas as obras (tabela)';
COMMENT ON VIEW analytics.v_metabase_dashboard_completo IS 'View consolidada para análise completa com todas as dimensões e indicadores';
