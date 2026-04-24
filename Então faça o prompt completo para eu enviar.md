<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Então faça o prompt completo para eu enviar

```text
Quero que você atue como um Engenheiro de Dados Sênior finalizando um projeto de portfólio chamado "Observatorio de Obras Publicas".

O MVP atual já está executável e faz:
✅ [STEP 0] validação de conexão
✅ [STEP 1] inicialização de schemas
✅ [STEP 2] ingestão API → data/raw/obras_raw_{timestamp}.json  
✅ [STEP 3] transform → data/processed/obras_normalized_{timestamp}.json
✅ [STEP 4] carga PostgreSQL raw + trusted

O que FALTA para fechar como portfólio forte:
1. **Etapa 5: Camada Analytics** - materializar fato + dimensões + KPIs
2. **Data Quality Checks** - nulos, duplicados, integridade
3. **Queries analíticas** - 8 KPIs prontos para dashboard
4. **README atualizado** - status honesto + screenshots + valor de negócio
5. **Teste end-to-end** - validar que tudo conecta

Seu objetivo: transformar o MVP técnico em projeto de portfólio completo, com analytics real e documentação para recrutador.

## O que entregar:

### 1. Arquivos novos/modificados:

**app/main.py** - Adicionar STEP 5 (analytics layer)
```

[STEP 5/5] analytics layer - fato + dimensões + 8 KPIs

```

**sql/006_data_quality_checks.sql** - Validações:
```

- % registros com campos obrigatórios nulos
- duplicatas por chave natural
- integridade referencial fato → dimensões
- frescor dos dados (delta ingestion_timestamp)

```

**sql/007_kpi_queries.sql** - 8 KPIs de obras públicas:
```

1. Total obras por status (concluída/em execução/paralisada)
2. Obras por UF/Região
3. Valor previsto por órgão
4. Atraso médio por tipo de obra
5. Top 10 fornecedores por volume
6. Evolução mensal obras iniciadas
7. % obras dentro do prazo
8. Concentração por município (Gini ou top 5)
```

**app/analytics/** - Novo módulo:
```

- kpi_generator.py
- data_quality.py

```

### 2. Validações obrigatórias:

```

✅ Pipeline executa 0→5 com logs estruturados
✅ Analytics tables são populadas
✅ 8 KPIs são computados e salvos
✅ Data quality report é gerado
✅ README mostra screenshots dos resultados

```

### 3. Estrutura final esperada:

```

observatorio-obras-publicas/
├── app/
│   ├── main.py                 \# 0→5 steps
│   ├── analytics/
│   │   ├── kpi_generator.py
│   │   └── data_quality.py
│   └── ... (existente)
├── sql/
│   ├── 006_data_quality.sql
│   └── 007_kpi_queries.sql
├── data/
│   ├── raw/           \# ✅
│   ├── processed/     \# ✅
│   └── analytics/     \# 🆕 kpi_results.json
├── reports/
│   └── data_quality_report.json  \# 🆕
└── README.md          \# 🆕 atualizado

```

### 4. KPIs obrigatórios (SQL pronto):

```

KPIs esperados para obras públicas:

1. QTD_OBRAS_STATUS: concluída/em_execucao/paralisada_orcada
2. OBRAS_POR_UF: group by uf
3. VALOR_PREVISTO_ORGAO: top 10 orgaos por valor
4. ATRASO_MEDIO: avg(dias_atraso) por tipo_obra
5. TOP_FORNECEDORES: top 10 por qtd_contratos
6. EVOLUCAO_MENSAL: obras_iniciadas por mes/ano
7. %_DENTRO_PRAZO: dentro_prazo / total_obras
8. CONCENTRACAO_MUNICIPIO: top 5 municipios por qtd_obras
```

### 5. Data Quality Checks obrigatórios:

```

1. NULL_CHECKS: % nulos em campos obrigatórios
2. DUPLICATES: qtd duplicatas por chave natural
3. FK_INTEGRITY: fato.localidade_id IN dim_localidade.id
4. FRESHNESS: max(ingestion_timestamp) > now() - 7 days
5. RANGE_CHECKS: datas válidas, valores > 0
```

## Requisitos técnicos:

```

✅ main.py: STEP 5 executa após STEP 4 com sucesso
✅ analytics/kpi_generator.py: 8 funções, uma por KPI
✅ analytics/data_quality.py: 5 validações com thresholds
✅ reports/data_quality_report.json: métricas + pass/fail
✅ docker-compose up app: executa 0→5 sem erro
✅ docker exec ... --max-pages 1: teste rápido OK

```

## README atualizado deve ter:

```

1. Problema de negócio (transparência obras públicas)
2. Arquitetura 3 camadas + analytics
3. Stack + Docker local
4. Como executar (passo a passo)
5. Screenshots: logs pipeline + data_quality_report.json
6. 8 KPIs listados com query SQL
7. Próximas evoluções (Metabase/Airflow/BigQuery)
```

## Formato da resposta:

```

1. Resumo: "Projeto completo com analytics + quality checks"
2. Arquivos novos: 👉 app/analytics/kpi_generator.py
3. Arquivos modificados: ✏️ app/main.py
4. SQL novo: 📊 sql/006_data_quality_checks.sql
5. README finalizado
6. Teste end-to-end: comandos para validar
7. Validation Notes: o que tester localmente
```

## Critérios de sucesso:

```

✅ docker-compose up app → STEP 0→5 ✅
✅ SELECT * FROM analytics.fato_obras LIMIT 10 → dados
✅ cat reports/data_quality_report.json → pass ✅
✅ 8 KPIs computados em analytics/kpi_results.json
✅ README explica valor para recrutador

```

Quero qualidade de portfólio sênior, executável e impactante para entrevista Data Engineer.
```


## Por que esse prompt fecha o projeto

1. **Completa o ciclo analytics** - fato + dimensões + 8 KPIs reais
2. **Adiciona data quality** - profissionaliza o pipeline
3. **Documenta valor** - README foca recrutador, não só código
4. **Testável** - comandos claros para validar end-to-end
5. **Evolutivo** - preparado para Metabase/Airflow depois

Depois que o Claude entregar isso, você terá um projeto **pronto para GitHub**, com ciclo completo raw→analytics + quality checks + documentação forte. Perfeito para entrevista! 🚀

