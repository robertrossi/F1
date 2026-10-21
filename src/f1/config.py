"""Configuração do cliente OpenF1."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    """Configuração de transporte da API."""

    base_url: str = "https://api.openf1.org/v1"
    timeout: float = 10.0

    def __post_init__(self) -> None:
        if not self.base_url.strip():
            raise ValueError("base_url não pode ser vazia")
        if self.timeout <= 0:
            raise ValueError("timeout deve ser maior que zero")
