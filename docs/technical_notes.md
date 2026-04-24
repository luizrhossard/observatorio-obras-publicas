# Technical Notes and Assumptions

## API Integration Notes

### Endpoint Assumptions
Based on the ObrasGov API documentation, the following endpoints are expected:

- `GET /consultar` - List all obras with pagination
- `GET /consultar/{id}` - Get single obra details

The exact JSON field names may vary. The normalizer includes multiple possible mappings for each field to handle variations:

```python
# Example field mappings handled
obra_id = raw.get("id") or raw.get("codigo") or raw.get("idObra")
nome = raw.get("nome") or raw.get("titulo")
valor_previsto = raw.get("valorPrevisto") or raw.get("valorInvestimento")
```

### Adaptation Strategy

If API fields change:

1. **Field Mapping**: Update `_normalize_obra()` in `normalize_obras.py`
2. **Status Values**: Modify `_normalize_status()` with new patterns
3. **Regions**: Update `valid_regions` dict

### Pagination

The API uses page-based pagination:
- Query params: `page=0`, `size=100`
- Response: `{ "content": [...], "totalPages": N }`

The client fetches all pages by default. Limit with `max_pages` parameter.

### Rate Limiting
- No API key required (public data)
- Consider adding rate limiting for production

## Database Design Considerations

### Surrogate vs Natural Keys
- **raw.obras_raw**: Uses `obra_id` (natural key) from source
- **trusted.obras**: Uses `obra_id` for idempotency
- **analytics**: Uses surrogate keys (auto-generated IDs)

### Data Type Decisions
- `valor_previsto`/`valor_executado`: DECIMAL(18, 2) for Brazilian currency
- `latitude`/`longitude`: DECIMAL for GPS coordinates
- JSONB for raw payloads (flexible schema)

## Future Evolution Paths

### Apache Airflow Integration
```python
# dag.py example structure
from airflow import DAG
from airflow.operators.python import PythonOperator

with DAG('obras_etl') as dag:
    ingest = PythonOperator(task_id='ingest', python_callable=run_ingestion)
    transform = PythonOperator(task_id='transform', python_callable=run_transform)
    load = PythonOperator(task_id='load', python_callable=run_load)
    
    ingest >> transform >> load
```

### dbt Integration
```sql
-- models/ trusted/obras.sql
SELECT 
    obra_id,
    nome,
    COALESCE(uf, 'N/A') as uf,
    CASE 
        WHEN status IN ('CONCLUIDA', 'PARALISADA', 'EM_EXECUCAO') 
        THEN status 
        ELSE 'OUTROS' 
    END as status_normalized
FROM raw.obras_raw
```

### BigQuery Migration
- Change connection to use `google-cloud-bigquery`
- Use partitioned tables by date
- Implement deduplication logic

### Streaming Evolution
- Replace batch with Kafka producers
- Add Spark Structured Streaming
- Implement CDC (Change Data Capture)

## Known Limitations

1. **API Availability**: No SLA guaranteed for public API
2. **Data Freshness**: Batch processing (not real-time)
3. **Error Handling**: Basic retry, no dead letter queue
4. **Monitoring**: No metrics dashboard yet

## Quick Fixes for Common Issues

### Issue: API Timeout
```env
API_TIMEOUT=60
API_MAX_RETRIES=5
```

### Issue: Large Dataset
```python
# Limit pages during development
obras = client.get_all_obras(max_pages=10)
```

### Issue: Missing Fields
Check normalizer field mappings and add alternatives.

## Testing Recommendations

```python
# test_normalize.py
def test_status_normalization():
    normalizer = ObraNormalizer()
    assert normalizer._normalize_status("EmAndamento") == "EM_EXECUCAO"
    assert normalizer._normalize_status("Concluída") == "CONCLUIDA"
    assert normalizer._normalize_status("Parada") == "PARALISADA"

def test_regiao_mapping():
    normalizer = ObraNormalizer()
    assert normalizer._get_regiao("SP") == "Sudeste"
    assert normalizer._get_regiao("BA") == "Nordeste"
```

## Monitoring and Observability

### Recommended Tools
- **Logs**: ELK Stack or CloudWatch
- **Metrics**: Prometheus + Grafana
- **Alerts**: PagerDuty or OpsGenie

### Key Metrics to Track
- Records ingested per run
- Transformation success rate
- Loading duration
- API error rate
- Database connection pool usage