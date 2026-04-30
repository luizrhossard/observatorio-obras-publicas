import os
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Config:
    api_base_url: str
    api_projects_endpoint: str
    api_timeout: int
    api_max_retries: int
    api_retry_delay: float
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    data_raw_dir: Path
    data_processed_dir: Path
    log_level: str

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            api_base_url=os.getenv(
                "API_BASE_URL", "https://api.obrasgov.gestao.gov.br/obrasgov/api"
            ),
            api_projects_endpoint=os.getenv("API_PROJECTS_ENDPOINT", "projeto-investimento"),
            api_timeout=int(os.getenv("API_TIMEOUT", "30")),
            api_max_retries=int(os.getenv("API_MAX_RETRIES", "3")),
            api_retry_delay=float(os.getenv("API_RETRY_DELAY", "1.0")),
            db_host=os.getenv("DB_HOST", "localhost"),
            db_port=int(os.getenv("DB_PORT", "5432")),
            db_name=os.getenv("DB_NAME", "obras_publicas"),
            db_user=os.getenv("DB_USER", "obras_user"),
            db_password=os.getenv("DB_PASSWORD", "obras_pass"),
            data_raw_dir=Path(os.getenv("DATA_RAW_DIR", "./data/raw")),
            data_processed_dir=Path(
                os.getenv("DATA_PROCESSED_DIR", "./data/processed")
            ),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )


config = Config.from_env()
