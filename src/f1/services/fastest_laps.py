"""Recupera e classifica as voltas mais rápidas em sessões de corrida."""

from __future__ import annotations

import logging
import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Protocol

LOGGER = logging.getLogger("f1.data")


class OpenF1Gateway(Protocol):
    """Parte do cliente OpenF1 usada pelo serviço de voltas rápidas."""

    def get_meetings(self, **filters: Any) -> list[dict[str, Any]]: ...

    def get_sessions(self, **filters: Any) -> list[dict[str, Any]]: ...

    def get_drivers(self, **filters: Any) -> list[dict[str, Any]]: ...

    def get_laps(self, **filters: Any) -> list[dict[str, Any]]: ...


@dataclass(frozen=True, slots=True)
class RaceSession:
    """Sessão principal de corrida associada ao circuito e ao GP."""

    circuit_key: str
    circuit_name: str
    meeting_key: str
    meeting_name: str
    session_key: str


@dataclass(frozen=True, slots=True)
class FastestLap:
    """Volta válida com seus dados de circuito, GP e piloto."""

    circuit_key: str
    circuit_name: str
    meeting_name: str
    session_key: str
    driver_number: str
    driver_name: str
    team_name: str
    lap_number: int
    lap_duration: float


class FastestLapService:
    """Consulta sessões e monta o top de voltas, recebendo o gateway por DI."""

    def __init__(self, gateway: OpenF1Gateway) -> None:
        self._gateway = gateway

    def race_sessions_for_year(self, year: int) -> tuple[RaceSession, ...]:
        """Lista apenas as sessões cujo tipo OpenF1 é ``Race``."""
        meetings = self._gateway.get_meetings(year=year)
        sessions_by_year = self._gateway.get_sessions(year=year)
        meetings_by_key = {
            str(meeting.get("meeting_key")): meeting
            for meeting in meetings
            if meeting.get("meeting_key") is not None
        }
        sessions: list[RaceSession] = []
        for session in sessions_by_year:
            meeting = meetings_by_key.get(str(session.get("meeting_key")))
            if meeting is None:
                continue
            meeting_key = meeting.get("meeting_key")
            circuit_key = meeting.get("circuit_key")
            circuit_name = meeting.get("circuit_short_name") or meeting.get(
                "circuit_name"
            )
            if not circuit_key:
                circuit_key = circuit_name
            if meeting_key is None or not circuit_key or not circuit_name:
                continue
            if str(session.get("session_type", "")).casefold() != "race":
                continue
            session_key = session.get("session_key")
            if session_key is None:
                continue
            sessions.append(
                RaceSession(
                    circuit_key=str(circuit_key),
                    circuit_name=str(circuit_name),
                    meeting_key=str(meeting_key),
                    meeting_name=str(meeting.get("meeting_name") or "Grande Prêmio"),
                    session_key=str(session_key),
                )
            )
        LOGGER.info(
            "Sessões de corrida carregadas",
            extra={
                "event": "race_sessions_loaded",
                "year": year,
                "count": len(sessions),
            },
        )
        return tuple(sessions)

    def fastest_laps(
        self,
        sessions: Sequence[RaceSession],
        circuit_key: str,
        *,
        limit: int = 5,
    ) -> tuple[FastestLap, ...]:
        """Retorna as melhores voltas válidas no circuito selecionado.

        Voltas sem duração, não numéricas, não finitas, não positivas e voltas
        de saída dos boxes são ignoradas. O limite não pode ser menor que um.
        """
        if limit < 1:
            raise ValueError("limit deve ser maior que zero")
        ranked: list[FastestLap] = []
        for session in sessions:
            if session.circuit_key != circuit_key:
                continue
            laps = self._gateway.get_laps(
                session_key=session.session_key,
                is_pit_out_lap=False,
            )
            if not laps:
                continue
            drivers = self._gateway.get_drivers(session_key=session.session_key)
            drivers_by_number = {
                str(driver.get("driver_number")): driver for driver in drivers
            }
            for lap in laps:
                duration = lap.get("lap_duration")
                if (
                    isinstance(duration, bool)
                    or not isinstance(duration, (int, float))
                    or not math.isfinite(duration)
                    or duration <= 0
                    or lap.get("is_pit_out_lap") is True
                ):
                    continue
                driver_number = str(lap.get("driver_number", ""))
                driver = drivers_by_number.get(driver_number, {})
                lap_number = lap.get("lap_number")
                if not driver_number or not isinstance(lap_number, int):
                    continue
                ranked.append(
                    FastestLap(
                        circuit_key=session.circuit_key,
                        circuit_name=session.circuit_name,
                        meeting_name=session.meeting_name,
                        session_key=session.session_key,
                        driver_number=driver_number,
                        driver_name=str(
                            driver.get("full_name") or f"Piloto {driver_number}"
                        ),
                        team_name=str(driver.get("team_name") or "—"),
                        lap_number=lap_number,
                        lap_duration=float(duration),
                    )
                )
        ranked.sort(
            key=lambda lap: (
                lap.lap_duration,
                lap.session_key,
                lap.driver_number,
                lap.lap_number,
            )
        )
        result = tuple(ranked[:limit])
        LOGGER.info(
            "Voltas rápidas classificadas",
            extra={
                "event": "fastest_laps_ranked",
                "circuit_key": circuit_key,
                "sessions": sum(
                    session.circuit_key == circuit_key for session in sessions
                ),
                "valid_laps": len(ranked),
                "returned": len(result),
            },
        )
        return result


def format_lap_time(seconds: float) -> str:
    """Formata segundos de volta como ``m:ss.mmm``."""
    if not math.isfinite(seconds) or seconds < 0:
        raise ValueError("tempo deve ser um número finito não negativo")
    minutes, remainder = divmod(seconds, 60)
    return f"{int(minutes)}:{remainder:06.3f}"
