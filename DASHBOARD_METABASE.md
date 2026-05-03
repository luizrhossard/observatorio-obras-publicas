# Dashboard de Obras Públicas no Metabase

Este documento explica como criar o dashboard de obras públicas no Metabase usando os dados do Observatório.

## Resumo do Dashboard

O dashboard deve conter:

| Componente | Tipo | Dados |
|------------|------|-------|
| **Cards de topo** | Number | Total de obras, Valor previsto, Valor executado |
| **Gráfico 1** | Pizza/Rosca | Obras por situação (Não iniciada, Em andamento, Paralisada, Concluída) |
| **Gráfico 2** | Barras | Obras por região/UF |
| **Gráfico 3** | Linha | Evolução de obras iniciadas/concluídas por mês |
| **Gráfico 4** | Barras horizontais | Top 10 órgãos com mais obras |
| **Tabela** | Tabela | Lista detalhada de todas as obras |

## Filtros do Dashboard

- **Período**: Ano/Mês de início da obra
- **Situação**: Filtro por status (Concluída, Em andamento, Paralisada, Não iniciada)
- **Região/UF**: Filtro por região brasileira ou estado

## Passo a Passo Rápido

### 1. Preparar os dados

```bash
# Executar o pipeline ETL para carregar dados no PostgreSQL
python app/main.py
```

### 2. Criar as views no banco

```bash
# No PostgreSQL, execute:
docker exec -i obras_postgres psql -U obras_user -d obras_publicas \
  -f sql/007_metabase_dashboard_views.sql
```

### 3. Conectar o Metabase

1. Acesse `http://localhost:3000` (ou onde o Metabase estiver rodando)
2. Vá em **Settings** → **Admin** → **Databases** → **Add database**
3. Configure:
   - Type: **PostgreSQL**
   - Display name: Observatório de Obras
   - Database: `obras_publicas`
   - Host: `postgres` (Docker) ou `localhost` (local)
   - Port: `5432`
   - Username: `obras_user`
   - Password: `obras_pass`
   - Schema: `analytics`

### 4. Criar o Dashboard

Para cada componente:

1. Clique em **New** → **Question**
2. Escolha a view correspondente (ex: `v_metabase_obras_por_situacao`)
3. Selecione o tipo de gráfico
4. Salve como **Card**
5. Adicione ao dashboard

### 5. Adicionar Filtros

No dashboard, clique em **Add a filter** e escolha:
- **Date/Time** → para período
- **Dropdown** → para situação e região

## Views Disponíveis

Use estas views diretamente no Metabase:

```sql
-- KPIs gerais (cards)
SELECT * FROM analytics.v_metabase_kpi_geral;

-- Pizza: Obras por situação
SELECT * FROM analytics.v_metabase_obras_por_situacao;

-- Barras: Obras por região
SELECT * FROM analytics.v_metabase_obras_por_regiao;

-- Linha: Evolução mensal
SELECT * FROM analytics.v_metabase_evolucao_mensal;

-- Top 10 órgãos
SELECT * FROM analytics.v_metabase_top_orgaos;

-- Tabela completa
SELECT * FROM analytics.v_metabase_lista_obras;
```

## Layout Sugerido

```
┌──────────────────────────────────────────────────────┐
│  [TOTAL OBRAS]  [VALOR PREVISTO]  [VALOR EXECUTADO] │
├──────────────────────────────────────────────────────┤
│  [PIZZA: SITUAÇÃO]     [BARRAS: REGIÃO]             │
├──────────────────────────────────────────────────────┤
│  [LINHA: EVOLUÇÃO MENSAL]                            │
├──────────────────────────────────────────────────────┤
│  [TOP 10 ÓRGÃOS]                                     │
├──────────────────────────────────────────────────────┤
│  [TABELA: LISTA DE OBRAS]                            │
└──────────────────────────────────────────────────────┘
```

## Documentação Completa

Para detalhes avançados, consulte:
- `docs/metabase_integration.md` - Guia completo de integração
- `sql/007_metabase_dashboard_views.sql` - Scripts das views

## Troubleshooting

**Dados não aparecem?**
```sql
-- Verificar se há dados nas tabelas
SELECT COUNT(*) FROM analytics.fact_obras;
SELECT COUNT(*) FROM trusted.obras;
```

**Views não aparecem no Metabase?**
- Verifique se o schema `analytics` está selecionado
- Execute novamente o script `007_metabase_dashboard_views.sql`
