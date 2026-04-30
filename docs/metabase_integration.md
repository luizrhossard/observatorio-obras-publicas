# Integração com Metabase - Dashboard de Obras Públicas

Este guia descreve como configurar o Metabase para visualizar os dados do Observatório de Obras Públicas.

## Pré-requisitos

1. **Pipeline ETL executado com sucesso** - Os dados devem estar carregados no PostgreSQL
2. **Views do Metabase criadas** - Execute o script `sql/007_metabase_dashboard_views.sql`
3. **Metabase instalado** - Docker ou instalação local

## Passo 1: Executar o Script das Views

```bash
# Conecte-se ao PostgreSQL e execute:
psql -U postgres -d observatorio_obras -f sql/007_metabase_dashboard_views.sql
```

Ou via Python:
```bash
python -m app.database.init_db
# E então execute o script SQL manualmente no pgAdmin ou psql
```

## Passo 2: Configurar Conexão no Metabase

### 2.1 Adicionar Banco de Dados

1. Acesse o Metabase (geralmente `http://localhost:3000`)
2. Vá em **Settings** (engrenagem) → **Admin** → **Databases** → **Add database**
3. Preencha os dados:

| Campo | Valor |
|-------|-------|
| Database type | PostgreSQL |
| Display name | Observatório de Obras |
| Database | `observatorio_obras` (ou o nome configurado) |
| Host | `localhost` (ou IP do servidor) |
| Port | `5432` |
| Username | `postgres` (ou usuário com acesso) |
| Password | Sua senha |
| Schema | `analytics` (principal para dashboards) |

4. Clique em **Save**

### 2.2 Configurar Schemas

No Metabase, vá em **Settings** → **Schemas** e certifique-se de que os seguintes schemas estão visíveis:
- `analytics` (principal para dashboards)
- `trusted` (dados normalizados)
- `raw` (dados brutos - opcional)

## Passo 3: Criar o Dashboard

### 3.1 Cards de KPI (Topo do Dashboard)

**Card 1: Total de Obras**
- Pergunta: `analytics.v_metabase_kpi_geral`
- Visualização: **Number**
- Campo: `total_obras`

**Card 2: Valor Total Previsto**
- Pergunta: `analytics.v_metabase_kpi_geral`
- Visualização: **Number**
- Campo: `valor_total_previsto`
- Formatação: Moeda (BRL)

**Card 3: Valor Total Executado**
- Pergunta: `analytics.v_metabase_kpi_geral`
- Visualização: **Number**
- Campo: `valor_total_executado`
- Formatação: Moeda (BRL)

### 3.2 Gráfico 1: Pizza - Obras por Situação

- Pergunta: `analytics.v_metabase_obras_por_situacao`
- Visualização: **Pie Chart** (ou Donut)
- Dimensão: `situacao`
- Métrica: `quantidade` ou `percentual`

### 3.3 Gráfico 2: Barras - Obras por Região

- Pergunta: `analytics.v_metabase_obras_por_regiao`
- Visualização: **Bar Chart**
- Dimensão: `regiao` (ou `uf`)
- Métrica: `quantidade_obras`

### 3.4 Gráfico 3: Linha - Evolução Mensal

- Pergunta: `analytics.v_metabase_evolucao_mensal`
- Visualização: **Line Chart**
- Eixo X: `ano` + `mes` (ou `data_inicio`)
- Eixo Y: `quantidade_obras`
- Série/Linha: `situacao` (para separar por status)

### 3.5 Gráfico 4: Barras Horizontais - Top Órgãos

- Pergunta: `analytics.v_metabase_top_orgaos`
- Visualização: **Bar Chart** (horizontal)
- Dimensão: `orgao_nome`
- Métrica: `quantidade_obras`

### 3.6 Tabela: Lista de Obras

- Pergunta: `analytics.v_metabase_lista_obras`
- Visualização: **Table**
- Colunas sugeridas:
  - `obra_id_origem`
  - `orgao`
  - `situacao`
  - `regiao`
  - `uf`
  - `valor_previsto`
  - `percentual_execucao`

## Passo 4: Adicionar Filtros ao Dashboard

No Metabase, adicione os seguintes filtros ao dashboard:

### Filtro de Período (Data)
- Tipo: **Date Filter**
- Campo: `ano_inicio` (de `v_metabase_dashboard_completo`)
- Ou use `data_inicio` da tabela `v_metabase_lista_obras`

### Filtro de Situação
- Tipo: **Dropdown** ou **Search Box**
- Campo: `situacao` (de `v_metabase_obras_por_situacao`)
- Valores disponíveis: View `analytics.v_metabase_filtro_situacao`

### Filtro de Região/UF
- Tipo: **Dropdown**
- Campo: `regiao` ou `uf`
- Valores disponíveis: View `analytics.v_metabase_filtro_regiao`

## Passo 5: Layout Sugerido do Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│  [Total Obras]  [Valor Previsto]  [Valor Executado]        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Pizza: Situação]          [Barras: Região]                │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Linha: Evolução Mensal]                                   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Top 10 Órgãos]                                            │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Tabela: Lista de Obras]                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Passo 6: Atualização de Dados

### Opção 1: Atualização Manual
Execute o pipeline ETL sempre que quiser atualizar os dados:
```bash
python app/main.py
```

### Opção 2: Agendamento com Cron (Linux/Mac)
```bash
# Editar crontab
crontab -e

# Adicionar execução diária às 6am
0 6 * * * cd /caminho/para/projeto && python app/main.py
```

### Opção 3: Agendador do Windows
Crie uma tarefa no **Task Scheduler** para executar:
```
python.exe C:\caminho\para\projeto\app\main.py
```

### Opção 4: Apache Airflow
Se usar Airflow, configure a DAG conforme documentado em `technical_notes.md`.

## Troubleshooting

### Problema: View não aparece no Metabase
**Solução:** Verifique se o schema `analytics` está selecionado nas configurações do banco.

### Problema: Dados desatualizados
**Solução:** Execute o pipeline ETL novamente e verifique se as views estão lendo das tabelas corretas.

### Problema: Erro de conexão
**Solução:** Verifique:
- PostgreSQL está rodando
- Credenciais estão corretas
- Firewall permite conexão na porta 5432

### Problema: Gráfico vazio
**Solução:** Verifique se há dados nas tabelas:
```sql
SELECT COUNT(*) FROM analytics.fact_obras;
SELECT COUNT(*) FROM trusted.obras;
```

## Views Disponíveis

| View | Descrição | Uso no Dashboard |
|------|-----------|------------------|
| `v_metabase_kpi_geral` | KPIs consolidados | Cards de topo |
| `v_metabase_obras_por_situacao` | Obras por status | Gráfico de pizza |
| `v_metabase_obras_por_regiao` | Obras por região/UF | Gráfico de barras |
| `v_metabase_evolucao_mensal` | Evolução temporal | Gráfico de linha |
| `v_metabase_top_orgaos` | Top 10 órgãos | Barras horizontais |
| `v_metabase_lista_obras` | Lista detalhada | Tabela |
| `v_metabase_dashboard_completo` | Dados completos | Análise ad-hoc |
| `v_metabase_filtro_situacao` | Opções de situação | Filtro dropdown |
| `v_metabase_filtro_regiao` | Opções de região | Filtro dropdown |
| `v_metabase_filtro_ano` | Opções de ano | Filtro dropdown |

## Dicas de Performance

1. **Índices**: As tabelas já possuem índices nas chaves estrangeiras
2. **Materialized Views**: Para datasets grandes, considere criar views materializadas
3. **Cache do Metabase**: Ative o cache em **Admin** → **Performance**
4. **Refresh**: Configure refresh automático em **Settings** → **Databases** → **Schedule**

## Exportação e Compartilhamento

- **Exportar dados**: Clique em **...** → **Download results** (CSV/XLSX)
- **Compartilhar dashboard**: Clique em **Share** → **Public link** (cuidado com dados sensíveis)
- **Alertas**: Configure pulses em **Subscriptions** para receber atualizações por email
