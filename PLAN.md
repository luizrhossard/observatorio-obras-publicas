## Objetivo
Adicionar integração com Metabase e criar views SQL para facilitar a construção de dashboards sobre as obras públicas.

## Contexto
Profissionalizar o projeto de portfólio, mostrando a camada de consumo/BI em cima do pipeline ETL.

## Impacto
- [x] Mudança no código (scripts/apply_views, integração Metabase)
- [x] Novas queries SQL para analytics (views de dashboard)
- [x] Documentação atualizada (README, DASHBOARD_METABASE.md)
- [x] Impacto relevante em performance/custo (apenas consultas de leitura — views são leves, sem materialized views necessárias)

## Como testar

```bash
docker-compose up -d postgres metabase
docker-compose up app

# Acessar Metabase em http://localhost:3000
# Configurar conexão com PostgreSQL (host: postgres, db: obras_publicas)
# Criar perguntas usando as views criadas
```