# Observatorio de Obras Publicas

Data Engineering Portfolio Project - End-to-end ETL pipeline for Brazilian public infrastructure data.

## Overview

This project consumes, transforms, and analyzes data from Brazil's ObrasGov API - the government public works database. It demonstrates professional data engineering practices suitable for a portfolio.

## Architecture

```
ObrasGov API -> Ingestion -> Raw (JSON) -> Transform -> Trusted (PostgreSQL) -> Analytics (KPIs)
```

- **Raw Layer**: JSON files with original API payloads
- **Trusted Layer**: Normalized PostgreSQL tables  
- **Analytics Layer**: KPIs and data quality checks

## Stack

- Python 3.11+
- PostgreSQL 15
- Docker & Docker Compose
- requests + psycopg2

## Quick Start

```bash
# Clone and run
git clone https://github.com/luizrhossard/observatorio-obras-publicas.git
cd observatorio-obras-publicas

# Start PostgreSQL
docker-compose up -d postgres

# Run pipeline
docker-compose up app
```

## Pipeline Steps

1. Validate database connection
2. Initialize schemas
3. Fetch from API (raw JSON)
4. Transform data
5. Load to PostgreSQL
6. Generate KPIs + Data Quality

## KPIs Generated

- Obras por status
- Obras por UF/Regiao
- Valor previsto por orgao
- Atraso medio
- Evolucao mensal
- % dentro do prazo
- Concentracao por municipio

## Outputs

- `data/raw/obras_raw_*.json` - Raw API data
- `data/processed/obras_normalized_*.json` - Transformed data  
- `data/analytics/kpi_results_*.json` - KPIs
- `data/reports/data_quality_report_*.json` - Data quality checks

## For Recruiters

This project demonstrates:
- ETL pipeline design
- PostgreSQL data modeling (raw/trusted/analytics)
- API integration with retry/backoff
- Data quality practices
- Docker containerization
- Python modular code

## License

MIT