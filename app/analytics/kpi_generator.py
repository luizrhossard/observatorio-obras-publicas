"""KPI Generator for Analytics Layer.

Computes 8 KPIs for obras publicas portfolio analysis.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.config import config
from app.database.connection import get_db_connection

logger = logging.getLogger(__name__)


def compute_kpi_status() -> List[Dict[str, Any]]:
    """
    KPI 1: Total obras por status.
    Returns: [{"status": "CONCLUIDA", "quantidade": 123, "valor": 5000000}, ...]
    """
    query = """
        SELECT 
            COALESCE(status, 'SEM_STATUS') AS status,
            COUNT(*) AS quantidade,
            SUM(COALESCE(valor_previsto, 0)) AS valor
        FROM trusted.obras
        GROUP BY status
        ORDER BY quantidade DESC
    """
    db = get_db_connection()
    with db.get_cursor() as cursor:
        cursor.execute(query)
        results = [dict(row) for row in cursor.fetchall()]
    logger.info(f"KPI 1 (status): {len(results)} statuses")
    return results


def compute_kpi_by_uf() -> List[Dict[str, Any]]:
    """
    KPI 2: Obras por UF/Região.
    Returns: [{"uf": "SP", "regiao": "Sudeste", "quantidade": 500}, ...]
    """
    query = """
        SELECT 
            COALESCE(uf, 'NI') AS uf,
            COALESCE(regiao, 'NaoInformado') AS regiao,
            COUNT(*) AS quantidade,
            SUM(COALESCE(valor_previsto, 0)) AS valor_previsto,
            SUM(COALESCE(valor_executado, 0)) AS valor_executado
        FROM trusted.obras
        GROUP BY uf, regiao
        ORDER BY quantidade DESC
    """
    db = get_db_connection()
    with db.get_cursor() as cursor:
        cursor.execute(query)
        results = [dict(row) for row in cursor.fetchall()]
    logger.info(f"KPI 2 (by_uf): {len(results)} UFs")
    return results


def compute_kpi_valor_orgao() -> List[Dict[str, Any]]:
    """
    KPI 3: Valor previsto por órgão (top 10).
    Returns: [{"orgao": "DNIT", "valor_total": 15000000, "qtd_obras": 50}, ...]
    """
    query = """
        SELECT 
            COALESCE(orgao, 'NaoIdentificado') AS orgao,
            SUM(COALESCE(valor_previsto, 0)) AS valor_total,
            COUNT(*) AS qtd_obras,
            AVG(COALESCE(valor_previsto, 0)) AS valor_medio
        FROM trusted.obras
        WHERE orgao IS NOT NULL
        GROUP BY orgao
        ORDER BY valor_total DESC
        LIMIT 10
    """
    db = get_db_connection()
    with db.get_cursor() as cursor:
        cursor.execute(query)
        results = [dict(row) for row in cursor.fetchall()]
    logger.info(f"KPI 3 (valor_orgao): {len(results)} orgaos")
    return results


def compute_kpi_atraso_medio() -> Optional[Dict[str, Any]]:
    """
    KPI 4: Atraso médio de obras.
    Returns: {"atraso_medio_dias": 45, "obras_atrasadas": 23, "total_obras_concluidas": 100}
    """
    query = """
        SELECT 
            AVG(
                CASE 
                    WHEN data_conclusao IS NOT NULL AND data_fim_previsto IS NOT NULL 
                    THEN EXTRACT(DAY FROM (data_conclusao - data_fim_previsto)
                    ELSE NULL
                END
            ) AS atraso_medio_dias,
            COUNT(*) FILTER (WHERE data_conclusao > data_fim_previsto) AS obras_atrasadas,
            COUNT(*) AS total_obras_concluidas
        FROM trusted.obras
        WHERE status = 'CONCLUIDA' 
          AND data_conclusao IS NOT NULL
    """
    db = get_db_connection()
    with db.get_cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            result = {
                "atraso_medio_dias": float(row[0]) if row[0] else 0,
                "obras_atrasadas": row[1],
                "total_obras_concluidas": row[2],
            }
            logger.info(f"KPI 4 (atraso): {result}")
            return result
    return None


def compute_kpi_evolucao_mensal() -> List[Dict[str, Any]]:
    """
    KPI 6: Evolução mensal de obras iniciadas.
    Returns: [{"ano_mes": "2024-01", "qtd_iniciadas": 50}, ...]
    """
    query = """
        SELECT 
            TO_CHAR(data_inicio, 'YYYY-MM') AS ano_mes,
            COUNT(*) AS qtd_iniciadas,
            SUM(COALESCE(valor_previsto, 0)) AS valor_total
        FROM trusted.obras
        WHERE data_inicio IS NOT NULL
        GROUP BY TO_CHAR(data_inicio, 'YYYY-MM')
        ORDER BY ano_mes DESC
        LIMIT 24
    """
    db = get_db_connection()
    with db.get_cursor() as cursor:
        cursor.execute(query)
        results = [dict(row) for row in cursor.fetchall()]
    logger.info(f"KPI 6 (evolucao): {len(results)} meses")
    return results


def compute_kpi_pct_dentro_prazo() -> Optional[Dict[str, Any]]:
    """
    KPI 7: % obras dentro do prazo.
    Returns: {"dentro_prazo": 75, "atrasadas": 25, "total": 100}
    """
    query = """
        SELECT 
            COUNT(*) AS total,
            COUNT(*) FILTER (WHERE data_conclusao <= data_fim_previsto) AS dentro_prazo,
            COUNT(*) FILTER (WHERE data_conclusao > data_fim_previsto) AS atrasadas,
            ROUND(
                COUNT(*) FILTER (WHERE data_conclusao <= data_fim_previsto)::NUMERIC * 100.0 / 
                NULLIF(COUNT(*), 0), 2
            ) AS pct_dentro_prazo
        FROM trusted.obras
        WHERE status = 'CONCLUIDA' 
          AND data_conclusao IS NOT NULL
          AND data_fim_previsto IS NOT NULL
    """
    db = get_db_connection()
    with db.get_cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            result = {
                "total": row[0],
                "dentro_prazo": row[1],
                "atrasadas": row[2],
                "pct_dentro_prazo": float(row[3]) if row[3] else 0,
            }
            logger.info(f"KPI 7 (prazo): {result}")
            return result
    return None


def compute_kpi_concentracao_municipio() -> List[Dict[str, Any]]:
    """
    KPI 8: Concentração por município (top 10).
    Returns: [{"municipio": "São Paulo", "uf": "SP", "qtd_obras": 150}, ...]
    """
    query = """
        SELECT 
            COALESCE(municipio, 'NaoInformado') AS municipio,
            COALESCE(uf, 'NI') AS uf,
            COUNT(*) AS qtd_obras,
            SUM(COALESCE(valor_previsto, 0)) AS valor_total
        FROM trusted.obras
        WHERE municipio IS NOT NULL
        GROUP BY municipio, uf
        ORDER BY qtd_obras DESC
        LIMIT 10
    """
    db = get_db_connection()
    with db.get_cursor() as cursor:
        cursor.execute(query)
        results = [dict(row) for row in cursor.fetchall()]
    logger.info(f"KPI 8 (concentracao): {len(results)} municipios")
    return results


def compute_kpi_regiao() -> List[Dict[str, Any]]:
    """
    KPI 5: Total de obras por região.
    Returns: [{"regiao": "Sudeste", "qtd_obras": 500, "valor": 15000000}, ...]
    """
    query = """
        SELECT 
            COALESCE(regiao, 'NaoInformado') AS regiao,
            COUNT(*) AS qtd_obras,
            SUM(COALESCE(valor_previsto, 0)) AS valor_total,
            SUM(COALESCE(valor_executado, 0)) AS valor_executado,
            ROUND(
                SUM(COALESCE(valor_executado, 0))::NUMERIC * 100.0 / 
                NULLIF(SUM(COALESCE(valor_previsto, 0)), 0), 2
            ) AS taxa_execucao
        FROM trusted.obras
        GROUP BY regiao
        ORDER BY qtd_obras DESC
    """
    db = get_db_connection()
    with db.get_cursor() as cursor:
        cursor.execute(query)
        results = [dict(row) for row in cursor.fetchall()]
    logger.info(f"KPI 5 (regiao): {len(results)} regioes")
    return results


def compute_all_kpis() -> Dict[str, Any]:
    """Compute all 8 KPIs and return as dict."""
    logger.info("Computing all KPIs...")

    kpis = {
        "kpi_1_status": compute_kpi_status(),
        "kpi_2_uf": compute_kpi_by_uf(),
        "kpi_3_valor_orgao": compute_kpi_valor_orgao(),
        "kpi_4_atraso_medio": compute_kpi_atraso_medio(),
        "kpi_5_regiao": compute_kpi_regiao(),
        "kpi_6_evolucao_mensal": compute_kpi_evolucao_mensal(),
        "kpi_7_pct_dentro_prazo": compute_kpi_pct_dentro_prazo(),
        "kpi_8_concentracao_municipio": compute_kpi_concentracao_municipio(),
        "computed_at": datetime.now().isoformat(),
    }

    logger.info("All KPIs computed successfully")
    return kpis


def save_kpis_to_file(kpis: Dict[str, Any], output_path: Path) -> Path:
    """Save KPIs to JSON file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(kpis, f, ensure_ascii=False, indent=2)

    logger.info(f"KPIs saved to {output_path}")
    return output_path


def main():
    """CLI entry point for KPI computation."""
    from app.utils.logger import setup_logger

    setup_logger("kpi_generator", "INFO")

    kpis = compute_all_kpis()

    # Save to analytics directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = (
        Path(config.data_processed_dir).parent
        / "analytics"
        / f"kpi_results_{timestamp}.json"
    )

    save_kpis_to_file(kpis, output_file)
    logger.info(f"KPIs computed: {len(kpis)} metrics")


if __name__ == "__main__":
    main()
