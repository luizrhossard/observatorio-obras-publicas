# Script para aplicar as views do Metabase via Docker
docker exec -i obras_postgres psql -U obras_user -d obras_publicas -f /docker-entrypoint-initdb.d/007_metabase_dashboard_views.sql
