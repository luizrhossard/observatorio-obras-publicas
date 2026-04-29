import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import requests

from app.config import config
from app.utils.logger import setup_logger

logger = setup_logger(__name__, config.log_level)


class ObrasGovClient:
    """Client for consuming ObrasGov API data."""

    def __init__(self):
        self.base_url = config.api_base_url
        self.projects_endpoint = config.api_projects_endpoint.strip("/")
        self.timeout = config.api_timeout
        self.max_retries = config.api_max_retries
        self.retry_delay = config.api_retry_delay
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": "Observatorio-Obras-Publicas/1.0",
            }
        )

    def _should_retry(self, response: requests.Response, retry_count: int) -> bool:
        """Determine if request should be retried."""
        if retry_count >= self.max_retries:
            return False

        # Retry on server errors (5xx)
        if response.status_code >= 500:
            return True

        # Retry on rate limiting (429)
        if response.status_code == 429:
            return True

        # Retry on temporary network errors
        if response.status_code in (502, 503, 504):
            return True

        return False

    def _get_retry_after(self, response: requests.Response, retry_count: int) -> float:
        """Get retry-after header or use exponential backoff."""
        # Respect Retry-After header if present
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return float(retry_after)
            except ValueError:
                pass

        # Exponential backoff: delay * (2 ^ retry_count)
        return self.retry_delay * (2**retry_count)

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"

        try:
            logger.debug(f"Request: {method} {url} params={params}")

            response = self.session.request(
                method=method, url=url, params=params, timeout=self.timeout
            )

            # Check if we should retry
            if self._should_retry(response, retry_count):
                delay = self._get_retry_after(response, retry_count)
                logger.warning(
                    f"Retryable error (attempt {retry_count + 1}/{self.max_retries}): "
                    f"status={response.status_code}, waiting {delay:.1f}s"
                )
                time.sleep(delay)
                return self._make_request(method, endpoint, params, retry_count + 1)

            response.raise_for_status()
            logger.info(f"Request successful: {method} {endpoint}")
            return response.json()

        except requests.exceptions.HTTPError as e:
            logger.warning(f"HTTP error (attempt {retry_count + 1}): {e}")
            raise

        except requests.exceptions.Timeout:
            if retry_count < self.max_retries:
                delay = self.retry_delay * (2**retry_count)
                logger.warning(f"Timeout (attempt {retry_count + 1}), waiting {delay}s")
                time.sleep(delay)
                return self._make_request(method, endpoint, params, retry_count + 1)
            raise

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

    def get_obras(
        self, page: int = 0, size: int = 100, filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Fetch list of obras (projects/investments)."""
        params = {"page": page, "size": size}

        if filters:
            params.update(filters)

        # The ObrasGov public API commonly exposes the projects list at `/projeto-investimento`.
        # Keep the endpoint configurable via `API_PROJECTS_ENDPOINT`.
        try:
            return self._make_request("GET", self.projects_endpoint, params=params)
        except requests.exceptions.HTTPError as e:
            response = getattr(e, "response", None)
            if response is not None and response.status_code == 404 and self.projects_endpoint != "consultar":
                # Backwards-compat fallback for older assumptions/docs.
                return self._make_request("GET", "consultar", params=params)
            raise

    def get_obra_by_id(self, obra_id: str) -> Dict[str, Any]:
        """Fetch single obra by ID."""
        # The API generally uses `idUnico` as a filter, returning a (possibly paginated) list.
        params = {"idUnico": obra_id, "page": 0, "size": 100}
        return self._make_request("GET", self.projects_endpoint, params=params)

    def get_all_obras(self, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """Fetch all obras with pagination."""
        all_obras = []
        page = 0

        while max_pages is None or page < max_pages:
            logger.info(f"Fetching page {page}...")

            response = self.get_obras(page=page)
            if isinstance(response, list):
                content = response
            else:
                content = response.get("content", [])

            if not content:
                break

            all_obras.extend(content)
            logger.info(f"Page {page}: {len(content)} obras (total: {len(all_obras)})")

            if len(content) < 100:
                break

            page += 1

        logger.info(f"Total obras fetched: {len(all_obras)}")
        return all_obras

    def fetch_and_save_raw(
        self, output_dir: Path, max_pages: Optional[int] = None
    ) -> Path:
        """Fetch all obras and save to raw JSON file."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"obras_raw_{timestamp}.json"

        logger.info(f"Fetching raw data to {output_file}...")

        obras = self.get_all_obras(max_pages=max_pages)

        raw_data = {
            "ingestion_timestamp": datetime.now().isoformat(),
            "record_count": len(obras),
            "source_system": "obrasgov",
            "source_url": self.base_url,
            "data": obras,
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Raw data saved: {output_file}")
        return output_file


def main():
    """CLI entry point for obra fetching."""
    from app.utils.logger import setup_logger

    setup_logger("obrasgov_client", "INFO")

    client = ObrasGovClient()
    output_dir = config.data_raw_dir
    output_file = client.fetch_and_save_raw(output_dir, max_pages=None)
    logger.info(f"Completed. Output: {output_file}")


if __name__ == "__main__":
    main()
