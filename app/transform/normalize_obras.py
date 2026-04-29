import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from app.config import config
from app.utils.logger import setup_logger

logger = setup_logger(__name__, config.log_level)


class ObraNormalizer:
    """Normalize and transform raw ObrasGov data."""

    def __init__(self):
        self.valid_statuses = [
            "EM_EXECUCAO",
            "CONCLUIDA",
            "PARALISADA",
            "PROJETO",
            "A_INICIAR",
        ]

        self.valid_regions = {
            "AC": "Norte",
            "AP": "Norte",
            "AM": "Norte",
            "PA": "Norte",
            "RO": "Norte",
            "RR": "Norte",
            "TO": "Norte",
            "AL": "Nordeste",
            "BA": "Nordeste",
            "CE": "Nordeste",
            "MA": "Nordeste",
            "PB": "Nordeste",
            "PE": "nordeste",
            "PI": "Nordeste",
            "RN": "Nordeste",
            "SE": "Nordeste",
            "DF": "Centro-Oeste",
            "GO": "Centro-Oeste",
            "MT": "Centro-Oeste",
            "MS": "Centro-Oeste",
            "ES": "Sudeste",
            "MG": "Sudeste",
            "RJ": "Sudeste",
            "SP": "Sudeste",
            "PR": "Sul",
            "RS": "Sul",
            "SC": "Sul",
        }

    def normalize_obra(self, raw_obra: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize a single obra record.

        Args:
            raw_obra: Raw obra record from API

        Returns:
            Normalized obra dictionary
        """
        obra_id = (
            raw_obra.get("id")
            or raw_obra.get("codigo")
            or raw_obra.get("idObra")
            or raw_obra.get("idUnico")
        )

        if not obra_id:
            logger.warning(f"Missing obra ID, skipping: {raw_obra}")
            return None

        normalized = {
            "obra_id": str(obra_id),
            "nome": raw_obra.get("nome", raw_obra.get("titulo", "")),
            "descricao": raw_obra.get("descricao", ""),
            "uf": raw_obra.get("uf") or raw_obra.get("Uf") or raw_obra.get("siglaUf", ""),
            "municipio": raw_obra.get("municipio", raw_obra.get("nomeMunicipio", "")),
            "orgao": raw_obra.get("orgao", raw_obra.get("nomeOrgao", "")),
            "orgao_id": raw_obra.get("orgaoId") or raw_obra.get("idOrgao"),
            "funcao": raw_obra.get("funcao", raw_obra.get("nomeFuncao", "")),
            "subfuncao": raw_obra.get("subfuncao", raw_obra.get("nomeSubfuncao", "")),
            "valor_previsto": self._parse_decimal(
                raw_obra.get("valorPrevisto") or raw_obra.get("valorInvestimento")
            ),
            "valor_executado": self._parse_decimal(
                raw_obra.get("valorExecutado") or raw_obra.get("valorGasto")
            ),
            "status": self._normalize_status(
                raw_obra.get("status") or raw_obra.get("situacao")
            ),
            "latitude": self._parse_decimal(raw_obra.get("latitude")),
            "longitude": self._parse_decimal(raw_obra.get("longitude")),
            "data_inicio": self._parse_date(
                raw_obra.get("dataInicio") or raw_obra.get("dataInicioObra")
            ),
            "data_fim_previsto": self._parse_date(
                raw_obra.get("dataFimPrevisto") or raw_obra.get("dataPrevistaTermino")
            ),
            "data_conclusao": self._parse_date(
                raw_obra.get("dataConclusao") or raw_obra.get("dataTerminoReal")
            ),
            "data_atualizacao": self._parse_date(
                raw_obra.get("dataAtualizacao") or raw_obra.get("ultimaAtualizacao")
            ),
            "fonte_recursos": raw_obra.get("fonteRecursos") or raw_obra.get("fonte"),
            "modalidade": raw_obra.get("modalidade") or raw_obra.get("tipoModalidade"),
            "regiao": self._get_regiao(raw_obra.get("uf") or raw_obra.get("Uf") or raw_obra.get("siglaUf")),
            "ingestion_timestamp": datetime.now().isoformat(),
            "raw_payload": json.dumps(raw_obra, ensure_ascii=False),
        }

        return normalized

    def _normalize_status(self, status: Optional[str]) -> str:
        """Normalize status to standard values."""
        if not status:
            return "DESCONHECIDO"

        status_upper = status.upper().replace(" ", "_")

        for valid in self.valid_statuses:
            if valid in status_upper:
                return valid

        if "EXEC" in status_upper or "ANDAM" in status_upper:
            return "EM_EXECUCAO"
        elif "CONCLUI" in status_upper:
            return "CONCLUIDA"
        elif "PARALIS" in status_upper:
            return "PARALISADA"
        elif "PROJETO" in status_upper:
            return "PROJETO"
        elif "INICIAR" in status_upper:
            return "A_INICIAR"

        return "DESCONHECIDO"

    def _get_regiao(self, uf: Optional[str]) -> Optional[str]:
        """Map UF to region."""
        if not uf:
            return None
        return self.valid_regions.get(uf.upper())

    def _parse_decimal(self, value: any) -> Optional[float]:
        """Parse decimal value from various formats."""
        if value is None:
            return None

        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            value = value.replace(".", "").replace(",", ".")
            try:
                return float(value)
            except ValueError:
                return None

        return None

    def _parse_date(self, value: any) -> Optional[str]:
        """Parse date to ISO format."""
        if not value:
            return None

        if isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                return dt.date().isoformat()
            except ValueError:
                return value

        return str(value)

    def normalize_batch(self, raw_obras: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize batch of raw obras.

        Args:
            raw_obras: List of raw obra records

        Returns:
            List of normalized obra records
        """
        normalized_obras = []

        for raw_obra in raw_obras:
            try:
                normalized = self.normalize_obra(raw_obra)
                if normalized:
                    normalized_obras.append(normalized)
            except Exception as e:
                logger.warning(f"Error normalizing obra: {e}")
                continue

        logger.info(f"Normalized {len(normalized_obras)}/{len(raw_obras)} obras")
        return normalized_obras

    def load_raw_and_transform(self, raw_file: Path) -> List[Dict[str, Any]]:
        """
        Load raw JSON file and transform.

        Args:
            raw_file: Path to raw JSON file

        Returns:
            List of normalized records
        """
        logger.info(f"Loading raw file: {raw_file}")

        with open(raw_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        obras = raw_data.get("data", raw_data.get("content", []))

        if not obras:
            logger.warning("No data found in raw file")
            return []

        return self.normalize_batch(obras)


def transform_raw_file(input_file: Path, output_file: Path) -> Path:
    """
    Transform raw data file to normalized format.

    Args:
        input_file: Input raw JSON file
        output_file: Output normalized JSON file

    Returns:
        Path to output file
    """
    normalizer = ObraNormalizer()

    normalized_obras = normalizer.load_raw_and_transform(input_file)

    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    transform_data = {
        "transform_timestamp": datetime.now().isoformat(),
        "record_count": len(normalized_obras),
        "data": normalized_obras,
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(transform_data, f, ensure_ascii=False, indent=2)

    logger.info(f"Transformed data saved: {output_file}")

    return output_file


def main():
    """CLI entry point for transformation."""
    from app.utils.logger import setup_logger

    setup_logger("normalize", "INFO")

    raw_dir = config.data_raw_dir
    processed_dir = config.data_processed_dir

    raw_files = sorted(Path(raw_dir).glob("obras_raw_*.json"))

    if not raw_files:
        logger.warning("No raw files found")
        return

    latest_raw = raw_files[-1]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = processed_dir / f"obras_normalized_{timestamp}.json"

    transform_raw_file(latest_raw, output_file)

    logger.info(f"Completed. Output: {output_file}")


if __name__ == "__main__":
    main()
