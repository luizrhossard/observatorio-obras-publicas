"""Data Quality Checks for Observatorio de Obras Publicas."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from app.config import config
from app.database.connection import get_db_connection

logger = logging.getLogger(__name__)


def check_nulls() -> Dict[str, Any]:
    """Check 1: NULL_CHECKS - % nulos em campos obrigatórios."""
    query = """
        SELECT 
            COUNT(*) AS total_registros,
            ROUND(COUNT(*) FILTER (WHERE nome IS NULL OR nome = '')::NUMERIC * 100.0 / NULLIF(COUNT(*), 0), 2) AS pct_nome_nulo,
            ROUND(COUNT(*) FILTER (WHERE uf IS NULL OR uf = '')::NUMERIC * 100.0 / NULLIF(COUNT(*), 0), 2) AS pct_uf_nulo,
            ROUND(COUNT(*) FILTER (WHERE status IS NULL OR status = '')::NUMERIC * 100.0 / NULLIF(COUNT(*), 0), 2) AS pct_status_nulo,
            ROUND(COUNT(*) FILTER (WHERE valor_previsto IS NULL)::NUMERIC * 100.0 / NULLIF(COUNT(*), 0), 2) AS pct_valor_nulo
        FROM trusted.obras
    """
    db = get_db_connection()
    with db.get_cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            result = {
                "total_registros": row[0],
                "pct_nome_nulo": float(row[1]) if row[1] else 0,
                "pct_uf_nulo": float(row[2]) if row[2] else 0,
                "pct_status_nulo": float(row[3]) if row[3] else 0,
                "pct_valor_nulo": float(row[4]) if row[4] else 0,
                "pass": float(row[1]) < 10 and float(row[2]) < 10,
            }
            return result
    return {"pass": False}


def check_duplicates() -> Dict[str, Any]:
    """Check 2: DUPLICATES - duplicatas por chave natural."""
    query = """
        SELECT COUNT(*) - COUNT(DISTINCT obra_id) AS duplicatas_count FROM trusted.obras
    """
    db = get_db_connection()
    with db.get_cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            result = {"duplicatas_count": row[0], "pass": row[0] == 0}
            return result
    return {"duplicatas_count": 0, "pass": True}


def check_fk_integrity() -> Dict[str, Any]:
    """Check 3: FK_INTEGRITY - UF válida."""
    valid_ufs = (
        "AC",
        "AP",
        "AM",
        "PA",
        "RO",
        "RR",
        "TO",
        "AL",
        "BA",
        "CE",
        "MA",
        "PB",
        "PE",
        "PI",
        "RN",
        "SE",
        "DF",
        "GO",
        "MT",
        "MS",
        "ES",
        "MG",
        "RJ",
        "SP",
        "PR",
        "RS",
        "SC",
    )
    query = f"""
        SELECT 
            COUNT(*) AS total,
            COUNT(*) FILTER (WHERE uf IN {valid_ufs}) AS uf_valida,
            ROUND(
                COUNT(*) FILTER (WHERE uf IN {valid_ufs})::NUMERIC * 100.0 / NULLIF(COUNT(*), 0), 2
            ) AS pct_valida
        FROM trusted.obras
    """
    db = get_db_connection()
    with db.get_cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            pct = float(row[2]) if row[2] else 0
            result = {
                "total_registros": row[0],
                "uf_valida": row[1],
                "pct_valida": pct,
                "pass": pct > 95,
            }
            return result
    return {"pct_valida": 0, "pass": False}


def check_freshness() -> Dict[str, Any]:
    """Check 4: FRESHNESS - dados recentes (até 30 dias)."""
    query = "SELECT MAX(ingestion_timestamp) AS ultima_ingestao FROM trusted.obras"
    db = get_db_connection()
    with db.get_cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchone()
        if row and row[0]:
            ultima = row[0]
            dias = (datetime.now() - ultima).days if ultima else 999
            result = {
                "ultima_ingestao": str(ultima),
                "dias_desde_ingestao": dias,
                "pass": dias <= 30,
            }
            return result
    return {"dias_desde_ingestao": 999, "pass": False}


def check_value_ranges() -> Dict[str, Any]:
    """Check 5: RANGE_CHECKS - valores válidos."""
    query = """
        SELECT 
            COUNT(*) AS total,
            COUNT(*) FILTER (WHERE valor_previsto < 0) AS valores_negativos,
            COUNT(*) FILTER (WHERE valor_executado < 0) AS exec_negativo,
            MIN(valor_previsto) AS min_valor,
            MAX(valor_previsto) AS max_valor
        FROM trusted.obras
    """
    db = get_db_connection()
    with db.get_cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            result = {
                "total_registros": row[0],
                "valores_negativos": row[1],
                "exec_negativo": row[2],
                "min_valor": float(row[3]) if row[3] else 0,
                "max_valor": float(row[4]) if row[4] else 0,
                "pass": row[1] == 0 and row[2] == 0,
            }
            return result
    return {"pass": True}


def run_data_quality_checks() -> Dict[str, Any]:
    """Run all 5 data quality checks."""
    logger.info("Running data quality checks...")

    report = {
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "null_checks": check_nulls(),
            "duplicates": check_duplicates(),
            "fk_integrity": check_fk_integrity(),
            "freshness": check_freshness(),
            "value_ranges": check_value_ranges(),
        },
    }

    all_pass = all(c.get("pass", False) for c in report["checks"].values())
    report["overall_pass"] = all_pass

    logger.info(f"Data quality: {'PASS' if all_pass else 'FAIL'}")
    return report


def save_report(report: Dict[str, Any], output_path: Path) -> Path:
    """Save report to JSON file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    logger.info(f"Report saved to {output_path}")
    return output_path


def main():
    """CLI entry point."""
    from app.utils.logger import setup_logger

    setup_logger("data_quality", "INFO")

    report = run_data_quality_checks()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = (
        Path(config.data_processed_dir).parent
        / "reports"
        / f"data_quality_report_{timestamp}.json"
    )

    save_report(report, output_file)
    logger.info(f"Overall: {'PASS' if report['overall_pass'] else 'FAIL'}")


if __name__ == "__main__":
    main()
