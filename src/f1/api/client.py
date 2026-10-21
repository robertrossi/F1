"""Cliente HTTP para endpoints de dados da OpenF1."""

from __future__ import annotations

import logging
import time
from collections.abc import Sequence
from typing import Any

import httpx

from f1.config import Settings

LOGGER = logging.getLogger("f1.api")


class OpenF1Error(Exception):
    """Erro base para falhas ao consultar a OpenF1."""


class OpenF1HTTPError(OpenF1Error):
    """Resposta HTTP de erro, incluindo status e endpoint consultado."""

    def __init__(self, status_code: int, endpoint: str) -> None:
        self.status_code = status_code
        self.endpoint = endpoint
        super().__init__(f"OpenF1 respondeu HTTP {status_code} em /{endpoint}")


class OpenF1ConnectionError(OpenF1Error):
    """Falha de rede ou timeout ao consultar a API."""


class OpenF1Client:
    """Cliente síncrono; aceita cliente httpx injetável para testes."""

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.settings = settings or Settings()
        self._owns_client = http_client is None
        self._client = http_client or httpx.Client(timeout=self.settings.timeout)

    def get(self, endpoint: str, **filters: Any) -> list[dict[str, Any]]:
        """Consulta endpoint e retorna registros JSON sem transformar os dados.

        Sequências de valores geram parâmetros repetidos. A codificação dos
        operadores de filtro é delegada ao httpx.
        """
        endpoint = endpoint.strip("/")
        if not endpoint or ".." in endpoint or "?" in endpoint:
            raise ValueError("endpoint deve ser um caminho simples da API")
        params: list[tuple[str, Any]] = []
        for key, value in filters.items():
            if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
                params.extend((key, item) for item in value)
            else:
                params.append((key, value))
        url = f"{self.settings.base_url.rstrip('/')}/{endpoint}"
        for attempt in range(3):
            try:
                response = self._client.get(url, params=params)
            except httpx.TimeoutException as exc:
                raise OpenF1ConnectionError(f"Timeout consultando /{endpoint}") from exc
            except httpx.RequestError as exc:
                message = f"Falha de conexão consultando /{endpoint}"
                raise OpenF1ConnectionError(message) from exc
            if response.status_code != 429 or attempt == 2:
                break
            retry_after = response.headers.get("Retry-After", "")
            try:
                delay = min(max(float(retry_after), 0.0), 5.0)
            except ValueError:
                delay = 0.5 * (2**attempt)
            LOGGER.warning(
                "OpenF1 limitou a frequência de consultas",
                extra={
                    "event": "openf1_rate_limited",
                    "endpoint": endpoint,
                    "attempt": attempt + 1,
                    "retry_delay_seconds": delay,
                },
            )
            response.close()
            time.sleep(delay)
        if response.is_error:
            raise OpenF1HTTPError(response.status_code, endpoint)
        try:
            payload = response.json()
        except ValueError as exc:
            raise OpenF1Error(f"Resposta inválida (JSON) em /{endpoint}") from exc
        if not isinstance(payload, list):
            raise OpenF1Error(f"Formato inesperado em /{endpoint}: esperado uma lista")
        if any(not isinstance(item, dict) for item in payload):
            raise OpenF1Error(
                f"Formato inesperado em /{endpoint}: esperado objetos JSON"
            )
        return payload

    def get_meetings(self, **filters: Any) -> list[dict[str, Any]]:
        """Consulta etapas e testes."""
        return self.get("meetings", **filters)

    def get_sessions(self, **filters: Any) -> list[dict[str, Any]]:
        """Consulta sessões."""
        return self.get("sessions", **filters)

    def get_drivers(self, **filters: Any) -> list[dict[str, Any]]:
        """Consulta pilotos."""
        return self.get("drivers", **filters)

    def get_laps(self, **filters: Any) -> list[dict[str, Any]]:
        """Consulta tempos e metadados de voltas."""
        return self.get("laps", **filters)

    def close(self) -> None:
        """Fecha o transporte quando pertence a este cliente."""
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> OpenF1Client:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
