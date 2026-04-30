@echo off
REM Script para aplicar as views do Metabase via Docker no Windows
docker exec -i obras_postgres psql -U obras_user -d obras_publicas -f /docker-entrypoint-initdb.d/007_metabase_dashboard_views.sql
pause
