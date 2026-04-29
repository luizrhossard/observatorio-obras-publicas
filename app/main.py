import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

from app.config import config
from app.utils.logger import setup_logger
from app.database.init_db import init_database, check_database_connection


def run_pipeline(
    skip_ingestion: bool = False,
    skip_transform: bool = False,
    skip_load: bool = False,
    max_pages: Optional[int] = None,
) -> bool:
    """
    Execute the complete ETL pipeline.

    Args:
        skip_ingestion: Skip API ingestion step
        skip_transform: Skip transformation step
        skip_load: Skip database load step
        max_pages: Limit pages fetched from API (None = all)

    Returns:
        True if successful, False otherwise
    """
    logger = setup_logger("pipeline", config.log_level)
    start_time = datetime.now()

    logger.info("=" * 60)
    logger.info("STARTING ETL PIPELINE")
    logger.info("=" * 60)

    # Step 0: Validate database connection
    logger.info("[STEP 0/5] Validating database connection...")
    if not check_database_connection():
        logger.error("Database connection unavailable")
        return False
    logger.info("[STEP 0/5] Database connection OK")

    # Step 1: Initialize database schema and tables
    logger.info("[STEP 1/5] Initializing database schema...")
    try:
        init_database()
        logger.info("[STEP 1/5] Database schema initialized")
    except Exception as e:
        logger.warning(f"Schema init warning (may already exist): {e}")

    extracted_count = 0
    transformed_count = 0
    loaded_count = 0

    try:
        # Step 2: Ingestion (fetch from API)
        if not skip_ingestion:
            logger.info("[STEP 2/5] Starting ingestion from API...")
            from app.ingestion.obrasgov_client import ObrasGovClient

            client = ObrasGovClient()
            raw_file = client.fetch_and_save_raw(
                config.data_raw_dir, max_pages=max_pages
            )

            # Get record count from saved file
            import json

            with open(raw_file, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                extracted_count = raw_data.get("record_count", 0)

            logger.info(f"[STEP 2/5] Extracted {extracted_count} records to {raw_file}")
        else:
            logger.info("[STEP 2/5] Skipping ingestion")

        # Step 3: Transformation
        if not skip_transform:
            logger.info("[STEP 3/5] Starting transformation...")
            from app.transform.normalize_obras import transform_raw_file

            # Find latest raw file
            raw_dir = Path(config.data_raw_dir)
            raw_files = sorted(raw_dir.glob("obras_raw_*.json"))
            if not raw_files:
                logger.error("No raw files found for transformation")
                return False

            latest_raw = raw_files[-1]

            # Output to processed directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = (
                config.data_processed_dir / f"obras_normalized_{timestamp}.json"
            )

            transformed_file = transform_raw_file(latest_raw, output_file)

            # Get count
            import json

            with open(transformed_file, "r", encoding="utf-8") as f:
                transform_data = json.load(f)
                transformed_count = transform_data.get("record_count", 0)

            logger.info(f"[STEP 3/5] Transformed {transformed_count} records")
        else:
            logger.info("[STEP 3/5] Skipping transformation")

        # Step 4: Load to PostgreSQL (trusted + raw)
        if not skip_load:
            logger.info("[STEP 4/5] Loading to PostgreSQL...")
            from app.load.postgres_loader import load_to_postgres

            # Find latest normalized file
            processed_dir = Path(config.data_processed_dir)
            processed_files = sorted(processed_dir.glob("obras_normalized_*.json"))
            if not processed_files:
                logger.error("No normalized files found for loading")
                return False

            latest_processed = processed_files[-1]
            loaded_count = load_to_postgres(latest_processed)

            logger.info(f"[STEP 4/5] Loaded {loaded_count} records")
        else:
            logger.info("[STEP 4/5] Skipping load")

        # Step 5: Analytics (KPIs + Data Quality)
        logger.info("[STEP 5/5] Computing KPIs...")
        from app.analytics.kpi_generator import compute_all_kpis, save_kpis_to_file
        from app.analytics.data_quality import run_data_quality_checks, save_report

        # Compute KPIs
        kpis = compute_all_kpis()

        # Save KPIs
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        kpi_file = (
            config.data_processed_dir.parent
            / "analytics"
            / f"kpi_results_{timestamp}.json"
        )
        save_kpis_to_file(kpis, kpi_file)

        # Data Quality checks
        logger.info("[STEP 5/5] Running data quality checks...")
        dq_report = run_data_quality_checks()

        # Save DQ report
        dq_file = (
            config.data_processed_dir.parent
            / "reports"
            / f"data_quality_report_{timestamp}.json"
        )
        save_report(dq_report, dq_file)

        logger.info(f"[STEP 5/5] KPI results: {kpi_file}")
        logger.info(f"[STEP 5/5] DQ report: {dq_file}")
        logger.info(
            f"[STEP 5/5] Overall DQ: {'PASS' if dq_report.get('overall_pass') else 'FAIL'}"
        )

    except Exception as e:
        logger.error(f"Pipeline failed at step: {e}")
        logger.exception(e)
        return False

    # Summary
    duration = (datetime.now() - start_time).total_seconds()
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETED SUCCESSFULLY")
    logger.info(f"  Records extracted: {extracted_count}")
    logger.info(f"  Records transformed: {transformed_count}")
    logger.info(f"  Records loaded: {loaded_count}")
    logger.info(f"  Duration: {duration:.2f}s")
    logger.info("=" * 60)

    return True


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Observatorio de Obras Publicas ETL")
    parser.add_argument(
        "--skip-ingestion", action="store_true", help="Skip API ingestion"
    )
    parser.add_argument(
        "--skip-transform", action="store_true", help="Skip transformation"
    )
    parser.add_argument("--skip-load", action="store_true", help="Skip database load")
    parser.add_argument(
        "--max-pages", type=int, default=None, help="Max API pages to fetch"
    )

    args = parser.parse_args()

    success = run_pipeline(
        skip_ingestion=args.skip_ingestion,
        skip_transform=args.skip_transform,
        skip_load=args.skip_load,
        max_pages=args.max_pages,
    )

    if success:
        logger = logging.getLogger("pipeline")
        logger.info("EXIT: SUCCESS")
        sys.exit(0)
    else:
        logger = logging.getLogger("pipeline")
        logger.error("EXIT: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
