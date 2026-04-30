import json
import logging
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

from app.config import config
from app.database.connection import get_db_connection

logger = logging.getLogger(__name__)


class PostgresLoader:
    """Load transformed data into PostgreSQL."""

    def __init__(self):
        self.db = get_db_connection()

    def load_normalized_obras(self, normalized_data: List[Dict[str, Any]]) -> int:
        """
        Load normalized obras into raw and trusted tables.

        Args:
            normalized_data: List of normalized obra records

        Returns:
            Number of records loaded
        """
        loaded_count = 0

        with self.db.get_cursor() as cursor:
            for obra in normalized_data:
                cursor.execute("SAVEPOINT load_obra")
                try:
                    self._insert_raw(cursor, obra)
                    self._insert_trusted(cursor, obra)
                    cursor.execute("RELEASE SAVEPOINT load_obra")
                    loaded_count += 1
                except Exception as e:
                    cursor.execute("ROLLBACK TO SAVEPOINT load_obra")
                    logger.warning(f"Error loading obra {obra.get('obra_id')}: {e}")
                    continue

        logger.info(f"Loaded {loaded_count}/{len(normalized_data)} obras")
        return loaded_count

    def _insert_raw(self, cursor, obra: Dict[str, Any]) -> None:
        """Insert into raw table."""
        sql = """
            INSERT INTO raw.obras_raw (
                obra_id, payload, ingestion_timestamp
            ) VALUES (
                %s, %s, %s
            )
            ON CONFLICT (obra_id) DO UPDATE SET
                payload = EXCLUDED.payload,
                ingestion_timestamp = EXCLUDED.ingestion_timestamp
        """
        cursor.execute(
            sql,
            (
                obra.get("obra_id"),
                json.dumps(obra, ensure_ascii=False),
                datetime.now().isoformat(),
            ),
        )

    def _insert_trusted(self, cursor, obra: Dict[str, Any]) -> None:
        """Insert into trusted table."""
        sql = """
            INSERT INTO trusted.obras (
                obra_id, nome, descricao, uf, municipio, orgao, orgao_id,
                funcao, subfuncao, valor_previsto, valor_executado,
                status, latitude, longitude, data_inicio, data_fim_previsto,
                data_conclusao, data_atualizacao, fonte_recursos, modalidade,
                regiao, ingestion_timestamp
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (obra_id) DO UPDATE SET
                nome = EXCLUDED.nome,
                descricao = EXCLUDED.descricao,
                uf = EXCLUDED.uf,
                municipio = EXCLUDED.municipio,
                orgao = EXCLUDED.orgao,
                orgao_id = EXCLUDED.orgao_id,
                funcao = EXCLUDED.funcao,
                subfuncao = EXCLUDED.subfuncao,
                valor_previsto = EXCLUDED.valor_previsto,
                valor_executado = EXCLUDED.valor_executado,
                status = EXCLUDED.status,
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                data_inicio = EXCLUDED.data_inicio,
                data_fim_previsto = EXCLUDED.data_fim_previsto,
                data_conclusao = EXCLUDED.data_conclusao,
                data_atualizacao = EXCLUDED.data_atualizacao,
                fonte_recursos = EXCLUDED.fonte_recursos,
                modalidade = EXCLUDED.modalidade,
                regiao = EXCLUDED.regiao,
                ingestion_timestamp = EXCLUDED.ingestion_timestamp
        """
        cursor.execute(
            sql,
            (
                obra.get("obra_id"),
                obra.get("nome"),
                obra.get("descricao"),
                obra.get("uf"),
                obra.get("municipio"),
                obra.get("orgao"),
                obra.get("orgao_id"),
                obra.get("funcao"),
                obra.get("subfuncao"),
                obra.get("valor_previsto"),
                obra.get("valor_executado"),
                obra.get("status"),
                obra.get("latitude"),
                obra.get("longitude"),
                obra.get("data_inicio"),
                obra.get("data_fim_previsto"),
                obra.get("data_conclusao"),
                obra.get("data_atualizacao"),
                obra.get("fonte_recursos"),
                obra.get("modalidade"),
                obra.get("regiao"),
                obra.get("ingestion_timestamp"),
            ),
        )

    def load_from_file(self, file_path: Path) -> int:
        """
        Load normalized data from JSON file.

        Args:
            file_path: Path to normalized JSON file

        Returns:
            Number of records loaded
        """
        logger.info(f"Loading from file: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        obras = data.get("data", [])

        return self.load_normalized_obras(obras)


def load_to_postgres(normalized_file: Path) -> int:
    """Load normalized data to PostgreSQL."""
    loader = PostgresLoader()
    return loader.load_from_file(normalized_file)


def main():
    """CLI entry point for loading."""
    from app.utils.logger import setup_logger

    setup_logger("postgres_loader", "INFO")

    processed_dir = config.data_processed_dir
    processed_files = sorted(Path(processed_dir).glob("obras_normalized_*.json"))

    if not processed_files:
        logger.warning("No normalized files found")
        return

    latest_file = processed_files[-1]
    count = load_to_postgres(latest_file)
    logger.info(f"Loaded {count} records")


if __name__ == "__main__":
    main()
