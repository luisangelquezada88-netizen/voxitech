"""Cliente HTTP para extracción de documentos con reintentos, rate limit y robots.txt."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests

from voxitech.utils.logging import get_logger

logger = get_logger()


@dataclass
class FetchResult:
    """Resultado de una petición HTTP."""

    url: str
    final_url: str
    status_code: int
    content: bytes
    headers: dict
    fetched_at: str
    content_type: str | None = None
    encoding: str | None = None
    error: str | None = None


class Fetcher:
    """Fetch HTTP con rate limit, reintentos con backoff y verificación de robots.txt."""

    def __init__(
        self,
        user_agent: str = "VoxiTech Lab AI research (contacto: investigador@example.com)",
        rate_limit_rps: float = 1.0,
        respect_robots_txt: bool = True,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
    ) -> None:
        self.user_agent = user_agent
        self.rate_limit_rps = rate_limit_rps
        self.respect_robots_txt = respect_robots_txt
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

        self._session = requests.Session()
        self._session.headers.update({"User-Agent": user_agent})
        self._last_request_time: float | None = None
        self._robots_cache: dict[str, RobotFileParser] = {}

    def _respect_rate_limit(self) -> None:
        """Espera el tiempo necesario para respetar el rate limit configurado."""
        if self.rate_limit_rps <= 0:
            return
        min_interval = 1.0 / self.rate_limit_rps
        if self._last_request_time is not None:
            elapsed = time.monotonic() - self._last_request_time
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)

    def _robots_allowed(self, url: str) -> bool:
        """Verifica si la URL está permitida por robots.txt del dominio."""
        if not self.respect_robots_txt:
            return True

        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        if base not in self._robots_cache:
            rp = RobotFileParser()
            rp.set_url(f"{base}/robots.txt")
            try:
                rp.read()
            except Exception as exc:  # noqa: BLE001
                logger.warning("No se pudo leer robots.txt de {base}: {exc}", base=base, exc=exc)
                self._robots_cache[base] = None
                return True
            self._robots_cache[base] = rp

        rp = self._robots_cache[base]
        if rp is None:
            return True
        return rp.can_fetch(self.user_agent, url)

    def fetch(self, url: str) -> FetchResult:
        """Descarga el contenido de una URL con reintentos y rate limit.

        Returns:
            FetchResult con contenido, metadatos HTTP y posible error.
        """
        if not self._robots_allowed(url):
            msg = f"URL bloqueada por robots.txt: {url}"
            logger.warning(msg)
            return FetchResult(
                url=url,
                final_url=url,
                status_code=0,
                content=b"",
                headers={},
                fetched_at=datetime.now(timezone.utc).isoformat(),
                error=msg,
            )

        self._respect_rate_limit()

        last_error: str | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info("Fetching {url} (intento {attempt}/{max_retries})", url=url, attempt=attempt, max_retries=self.max_retries)
                response = self._session.get(url, timeout=self.timeout)
                response.raise_for_status()

                self._last_request_time = time.monotonic()

                content_type = response.headers.get("Content-Type")
                encoding = response.encoding or "utf-8"

                return FetchResult(
                    url=url,
                    final_url=str(response.url),
                    status_code=response.status_code,
                    content=response.content,
                    headers=dict(response.headers),
                    fetched_at=datetime.now(timezone.utc).isoformat(),
                    content_type=content_type,
                    encoding=encoding,
                )
            except requests.RequestException as exc:
                last_error = str(exc)
                logger.warning("Error en intento {attempt} para {url}: {error}", attempt=attempt, url=url, error=exc)
                if attempt < self.max_retries:
                    sleep_time = self.backoff_factor ** attempt
                    logger.info("Reintentando en {sleep_time}s", sleep_time=sleep_time)
                    time.sleep(sleep_time)

        logger.error("Fallo tras {max_retries} intentos para {url}: {error}", max_retries=self.max_retries, url=url, error=last_error)
        return FetchResult(
            url=url,
            final_url=url,
            status_code=0,
            content=b"",
            headers={},
            fetched_at=datetime.now(timezone.utc).isoformat(),
            error=last_error or "Unknown fetch error",
        )