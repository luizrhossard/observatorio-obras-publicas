# Observatorio de Obras Publicas

**Data Engineering Portfolio Project**

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue)
![Docker](https://img.shields.io/badge/Docker-ready-blue)

End-to-end data pipeline that consumes, transforms, and analyzes public infrastructure investment data from Brazil's ObrasGov API.

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   API Source     │────▶│   Ingestion      │────▶│   Raw Storage   │
│   (ObrasGov)     │     │   (HTTP Client)  │     │   (JSON files)  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Analytics     │◀────│   Load           │◀────│   Transform     │
│   (KPIs/Views)  │     │   (PostgreSQL)    │     │   (Normalization)│
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## Project Structure

```
observatorio-obras-publicas/
├── app/
│   ├── config.py              # Configuration management
│   ├── main.py              # Pipeline orchestration
│   ├── database/
│   │   ├── connection.py   # PostgreSQL connection pool
│   │   └── init_db.py       # Schema initialization
│   ├── ingestion/
│   │   └── obrasgov_client.py  # API client
│   ├── load/
│   │   └── postgres_loader.py # Data loading
│   ├── transform/
│   │   └── normalize_obras.py  # Data transformation
│   └── utils/
│       └── logger.py         # Logging utilities
├── sql/
│   ├── 001_create_schemas.sql
│   ├── 002_create_raw_tables.sql
│   ├── 003_create_trusted_tables.sql
│   ├── 004_create_analytics_tables.sql
│   └── 005_kpi_queries.sql
├── data/
│   ├── raw/                 # Raw JSON files
│   └── processed/           # Normalized data
├── docs/
│   └── architecture.md
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Technology Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.11+ |
| Database | PostgreSQL 15 |
| Container | Docker & Docker Compose |
| HTTP Client | requests |
| DB Driver | psycopg2 |

## Data Pipeline Architecture

The project follows a **medallion architecture** with three layers:

### 1. Raw Layer (`raw`)
- Stores complete JSON payloads from API
- Preserves original data structure
- Includes metadata: `ingestion_timestamp`, `source_system`
- Enables reprocessing from raw data

### 2. Trusted Layer (`trusted`)
- Normalized and validated data
- Standardized field names
- Data type conversions
- Status normalization
- Region mapping (UF → Region)

### 3. Analytics Layer (`analytics`)
- **Fact Table**: `fact_obras`
- **Dimensions**: `dim_orgao`, `dim_localidade`, `dim_status`, `dim_tempo`
- **Views**: Pre-computed KPIs

## Features

### Ingestion
- Retry mechanism with exponential backoff
- Request timeout handling
- Pagination support
- Error handling and logging
- Raw data persistence

### Transformation
- Flexible field mapping (multiple possible field names)
- Status standardization
- Region mapping (27 Brazilian UFs → 5 regions)
- Date parsing (multiple formats)
- Decimal parsing

### Loading
- Upsert operations (INSERT ON CONFLICT)
- Connection pooling
- Transaction management

### Analytics
- 8+ KPI queries included
- Pre-built views
- Support for temporal analysis

## KPIs Included

1. **Obras por Status** - Quantity by status (CONCLUIDA, EM_EXECUCAO, PARALISADA, etc.)
2. **Obras por UF** - Quantity by Brazilian state
3. **Valor Previsto por Órgão** - Total planned value by government agency
4. **Total por Região** - Summary by region (Norte, Nordeste, Sul, Sudeste, Centro-Oeste)
5. **Obras Concluídas vs Paralisadas vs Em Execução** - Status comparison
6. **Evolução Temporal** - Yearly trends
7. **Top 10 Municípios** - Most active cities
8. **Taxa de Execução** - Execution rate by region

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)

### Using Docker Compose

```bash
# 1. Clone and navigate to project
cd observatorio-obras-publicas

# 2. Create environment file
cp .env.example .env

# 3. Start infrastructure
docker-compose up -d postgres

# 4. Initialize database
docker-compose up app

# 5. Run pipeline
docker-compose up
```

### Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up PostgreSQL
docker run -d -p 5432:5432 -e POSTGRES_DB=obras_publicas \
    -e POSTGRES_USER=obras_user -e POSTGRES_PASSWORD=obras_pass postgres:15

# 3. Run SQL migrations
psql -h localhost -U obras_user -d obras_publicas -f sql/001_create_schemas.sql
# ... (run all SQL files)

# 4. Run pipeline steps
python -m app.ingestion.obrasgov_client   # Fetch raw data
python -m app.transform.normalize_obras   # Transform data
python -m app.load.postgres_loader       # Load to database
```

## Configuration

All configuration is managed via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | localhost | PostgreSQL host |
| `DB_PORT` | 5432 | PostgreSQL port |
| `DB_NAME` | obras_publicas | Database name |
| `DB_USER` | obras_user | Database user |
| `DB_PASSWORD` | obras_pass | Database password |
| `API_BASE_URL` | https://api.obrasgov.gestao.gov.br/obrasgov/api | API base URL |
| `API_TIMEOUT` | 30 | Request timeout (seconds) |
| `API_MAX_RETRIES` | 3 | Maximum retry attempts |
| `LOG_LEVEL` | INFO | Logging level |

## Sample Output

### KPI Query Results

```sql
-- Obras por status
       status        | quantidade
--------------------+-----------
 EM_EXECUCAO         |      1523
 CONCLUIDA           |       891
 PARALISADA         |       234
 PROJETO            |       156
 A_INICIAR          |        89

-- Obras por região
    regiao    | total_obras |   valor_total
------------+-----------+--------------
 Sudeste    |      1245 | 150000000.00
 Nordeste  |       890 |  85000000.00
 Sul        |       567 |  42000000.00
 Norte      |       234 |  18000000.00
 Centro-Oeste |    167 |  15000000.00
```

## Database Schema

### Schemas
- `raw` - Raw ingested data
- `trusted` - Normalized cleaned data
- `analytics` - Business analysis layer

### Main Tables

| Table | Schema | Description |
|-------|-------|-------------|
| `raw.obras_raw` | raw | JSON payloads |
| `trusted.obras` | trusted | Normalized records |
| `analytics.fact_obras` | analytics | Fact table |
| `analytics.dim_orgao` | analytics | Agency dimension |
| `analytics.dim_localidade` | analytics | Location dimension |
| `analytics.dim_status` | analytics | Status dimension |
| `analytics.dim_tempo` | analytics | Time dimension |

## Business Context

### Problem Statement
Brazil's government invests billions annually in infrastructure projects through the ObrasGov program. This project enables:

- **Transparency** - Public access to infrastructure investment data
- **Accountability** - Track project status and execution
- **Decision Making** - Identify patterns and anomalies
- **Control Quality** - Monitor execution rates across regions

### Use Cases
- Portfolio analysis for infrastructure investments
- Regional comparison of project execution
- Agency performance benchmarking
- Temporal trend analysis

## Future Enhancements

This project is designed for evolution:

### Phase 2
- Apache Airflow for orchestration
- dbt for transformations
- Google BigQuery for analytics
- Looker Studio for visualization

### Phase 3
- Real-time streaming with Kafka
- Data quality checks with Great Expectations
- Prometheus/Grafana monitoring
- Airflow DAG scheduling

### Phase 4
- CI/CD pipeline with GitHub Actions
- Infrastructure as Code (Terraform)
- Snowflake as data warehouse
- Containerized dbt

## Contributing

This is a portfolio project. Feel free to:
- Fork and customize
- Add new data sources
- Improve transformation logic
- Expand analytics queries

## License

MIT License - See LICENSE file for details.

## Disclaimer

This project uses public data from Brazil's government APIs.
Data accuracy depends on source systems.#   o b s e r v a t � r i o - o b r a s - p u b l i c a s  
 #   o b s e r v a t � r i o - o b r a s - p u b l i c a s  
 