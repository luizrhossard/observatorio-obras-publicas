import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from typing import Any, Optional
import logging

from app.config import config

logger = logging.getLogger(__name__)

ConnectionPool = Any


class DatabaseConnection:
    """PostgreSQL connection pool manager."""

    _instance: Optional["DatabaseConnection"] = None
    _connection_pool: Optional[ConnectionPool] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._connection_pool is None:
            self._initialize_pool()

    def _initialize_pool(self):
        try:
            self._connection_pool = pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                host=config.db_host,
                port=config.db_port,
                database=config.db_name,
                user=config.db_user,
                password=config.db_password,
            )
            logger.info(
                f"Database connection pool initialized: {config.db_host}:{config.db_port}/{config.db_name}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise

    @contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = self._connection_pool.getconn()
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                self._connection_pool.putconn(conn)

    @contextmanager
    def get_cursor(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
            finally:
                cursor.close()

    def close_all(self):
        if self._connection_pool:
            self._connection_pool.closeall()
            logger.info("Database connection pool closed")


def get_db_connection() -> DatabaseConnection:
    return DatabaseConnection()
