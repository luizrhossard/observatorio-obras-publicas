"""Analytics module for Observatorio de Obras Publicas."""

from app.analytics.kpi_generator import compute_all_kpis, save_kpis_to_file
from app.analytics.data_quality import run_data_quality_checks, save_report

__all__ = [
    "compute_all_kpis",
    "save_kpis_to_file",
    "run_data_quality_checks",
    "save_report",
]
