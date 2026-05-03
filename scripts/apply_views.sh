#!/bin/bash
# Script para aplicar as views do Metabase via Docker
# Uso: bash scripts/apply_views.sh

set -e

echo "Aplicando views do Metabase no PostgreSQL..."
docker exec -i obras_postgres psql -U obras_user -d obras_publicas \
  < sql/007_metabase_dashboard_views.sql

echo "Views aplicadas com sucesso!"
