import logging
from pathlib import Path
from typing import List

from app.database.connection import get_db_connection

logger = logging.getLogger(__name__)


def get_sql_files() -> List[Path]:
    """Get all SQL files from sql/ directory, sorted by filename."""
    sql_dir = Path(__file__).parent.parent.parent / "sql"
    return sorted(sql_dir.glob("*.sql"))


def execute_sql_file(cursor, file_path: Path) -> None:
    """Execute a single SQL file."""
    logger.info(f"Executing SQL file: {file_path.name}")

    with open(file_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    statements = [s.strip() for s in sql_content.split(";") if s.strip()]

    for statement in statements:
        try:
            cursor.execute(statement)
            logger.debug(f"Executed: {statement[:50]}...")
        except Exception as e:
            logger.warning(f"Error executing statement (may be expected): {e}")


def init_database():
    """Initialize database schema and tables."""
    logger.info("Starting database initialization...")

    sql_dir = Path(__file__).parent.parent.parent / "sql"

    if not sql_dir.exists():
        logger.error(f"SQL directory not found: {sql_dir}")
        raise FileNotFoundError(f"SQL directory not found: {sql_dir}")

    sql_files = sorted(sql_dir.glob("*.sql"))

    if not sql_files:
        logger.error("No SQL files found in sql/ directory")
        raise FileNotFoundError("No SQL files found")

    db = get_db_connection()

    with db.get_cursor() as cursor:
        for sql_file in sql_files:
            logger.info(f"Processing: {sql_file.name}")
            execute_sql_file(cursor, sql_file)

    logger.info("Database initialization completed successfully")


def check_database_connection() -> bool:
    """Verify database connection is working."""
    try:
        db = get_db_connection()
        with db.get_cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            logger.info(f"Database connected: {version[0]}")
            return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


if __name__ == "__main__":
    from app.utils.logger import setup_logger

    setup_logger("init_db", "INFO")

    if check_database_connection():
        init_database()
    else:
        logger.error("Cannot initialize database: connection check failed")
        exit(1)
