@echo off
REM Script para aplicar as views do Metabase via Docker no Windows
REM Uso: scripts\apply_views.bat

echo Aplicando views do Metabase no PostgreSQL...
docker exec -i obras_postgres psql -U obras_user -d obras_publicas ^
  < sql\007_metabase_dashboard_views.sql

echo Views aplicadas com sucesso!
pause
