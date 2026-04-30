"""
Script para aplicar as views do Metabase no banco de dados.
"""
import sys
from pathlib import Path

# Adicionar raiz ao path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.config import config
from app.database.connection import get_connection


def apply_views():
    """Aplica as views do Metabase no banco de dados."""

    # Caminho do script SQL
    sql_file = ROOT_DIR / "sql" / "007_metabase_dashboard_views.sql"

    if not sql_file.exists():
        print(f"Erro: Arquivo SQL não encontrado: {sql_file}")
        return False

    print(f"Lendo script SQL: {sql_file}")
    with open(sql_file, "r", encoding="utf-8") as f:
        sql_script = f.read()

    # Conectar e executar
    print("Conectando ao banco de dados...")
    conn = get_connection()

    if conn is None:
        print("Erro: Não foi possível conectar ao banco de dados")
        return False

    try:
        cursor = conn.cursor()
        print("Executando script SQL...")
        cursor.execute(sql_script)
        conn.commit()
        cursor.close()
        conn.close()
        print("Views aplicadas com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao executar script: {e}")
        conn.rollback()
        conn.close()
        return False


if __name__ == "__main__":
    success = apply_views()
    sys.exit(0 if success else 1)
