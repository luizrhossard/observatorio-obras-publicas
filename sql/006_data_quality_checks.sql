-- 006_data_quality_checks.sql
-- Data Quality validation queries

-- Check 1: NULL_CHECKS - percentual de nulos em campos obrigatórios
SELECT 
    COUNT(*) AS total_registros,
    ROUND(COUNT(*) FILTER (WHERE nome IS NULL OR nome = '')::NUMERIC * 100.0 / NULLIF(COUNT(*), 0), 2) AS pct_nome_nulo,
    ROUND(COUNT(*) FILTER (WHERE uf IS NULL OR uf = '')::NUMERIC * 100.0 / NULLIF(COUNT(*), 0), 2) AS pct_uf_nulo,
    ROUND(COUNT(*) FILTER (WHERE status IS NULL OR status = '')::NUMERIC * 100.0 / NULLIF(COUNT(*), 0), 2) AS pct_status_nulo,
    ROUND(COUNT(*) FILTER (WHERE valor_previsto IS NULL)::NUMERIC * 100.0 / NULLIF(COUNT(*), 0), 2) AS pct_valor_nulo
FROM trusted.obras;

-- Check 2: DUPLICATES - duplicatas por chave natural
SELECT 
    COUNT(*) - COUNT(DISTINCT obra_id) AS duplicatas_count
FROM trusted.obras;

-- Check 3: FK_INTEGRITY - UF válida
SELECT 
    COUNT(*) AS total,
    COUNT(*) FILTER (
        WHERE uf IN ('AC','AP','AM','PA','RO','RR','TO','AL','BA','CE','MA','PB','PE','PI','RN','SE',
                   'DF','GO','MT','MS','ES','MG','RJ','SP','PR','RS','SC')
    ) AS uf_valida,
    ROUND(
        COUNT(*) FILTER (
            WHERE uf IN ('AC','AP','AM','PA','RO','RR','TO','AL','BA','CE','MA','PB','PE','PI','RN','SE',
                       'DF','GO','MT','MS','ES','MG','RJ','SP','PR','RS','SC')
        )::NUMERIC * 100.0 / NULLIF(COUNT(*), 0), 2
    ) AS pct_valida
FROM trusted.obras;

-- Check 4: FRESHNESS - dados recentes
SELECT 
    MAX(ingestion_timestamp) AS ultima_ingestao,
    NOW() - MAX(ingestion_timestamp) AS dias_desde_ingestao
FROM trusted.obras;

-- Check 5: RANGE_CHECKS - valores válidos
SELECT 
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE valor_previsto < 0) AS valores_negativos,
    COUNT(*) FILTER (WHERE valor_executado < 0) AS exec_negativo,
    COUNT(*) FILTER (WHERE valor_executado > valor_previsto * 1.5) AS exec_acima_150,
    MIN(valor_previsto) AS min_valor,
    MAX(valor_previsto) AS max_valor
FROM trusted.obras;