"""Dashboard Streamlit com ranking das cinco voltas mais rápidas por circuito."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

import streamlit as st

from f1.api.client import OpenF1Client, OpenF1Error
from f1.logging_config import configure_logging
from f1.services.fastest_laps import (
    FastestLap,
    FastestLapService,
    RaceSession,
    format_lap_time,
)

LOGGER = logging.getLogger("f1.dashboard")
CACHE_TTL_SECONDS = 6 * 60 * 60


@st.cache_data(ttl=CACHE_TTL_SECONDS, max_entries=12, show_spinner=False)
def _load_race_sessions(year: int) -> tuple[RaceSession, ...]:
    with OpenF1Client() as client:
        return FastestLapService(client).race_sessions_for_year(year)


@st.cache_data(ttl=CACHE_TTL_SECONDS, max_entries=48, show_spinner=False)
def _load_top_five(
    sessions: tuple[RaceSession, ...], circuit_key: str
) -> tuple[FastestLap, ...]:
    with OpenF1Client() as client:
        return FastestLapService(client).fastest_laps(sessions, circuit_key)


def _table_rows(laps: tuple[FastestLap, ...]) -> list[dict[str, object]]:
    return [
        {
            "Posição": index,
            "Piloto": f"{lap.driver_name} (#{lap.driver_number})",
            "Equipe": lap.team_name,
            "Tempo": format_lap_time(lap.lap_duration),
            "Grande Prêmio": lap.meeting_name,
            "Volta": lap.lap_number,
        }
        for index, lap in enumerate(laps, start=1)
    ]


def main() -> None:
    """Renderiza o dashboard; deve ser iniciado pelo comando Streamlit."""
    configure_logging()
    st.set_page_config(
        page_title="F1 · Voltas mais rápidas",
        page_icon="🏎️",
        layout="wide",
    )
    st.title("F1 · Voltas mais rápidas")
    st.caption(
        "Top 5 de voltas válidas em sessões de corrida por circuito e temporada. "
        "Treinos, classificação e sprint ficam fora do ranking."
    )

    current_year = datetime.now(UTC).year
    years = list(range(2023, current_year + 1))
    selected_year = st.selectbox(
        "Temporada",
        years,
        index=len(years) - 1,
        help="O histórico gratuito da OpenF1 começa em 2023.",
    )
    try:
        with st.spinner("Carregando sessões de corrida da temporada…"):
            sessions = _load_race_sessions(selected_year)
    except OpenF1Error as exc:
        LOGGER.error(
            "Falha ao carregar sessões",
            extra={
                "event": "race_sessions_load_failed",
                "year": selected_year,
                "error": str(exc),
            },
        )
        st.error(f"Não foi possível carregar as sessões: {exc}")
        return
    except Exception:
        LOGGER.exception(
            "Erro inesperado ao carregar sessões",
            extra={"event": "race_sessions_load_unexpected", "year": selected_year},
        )
        st.error("Ocorreu um erro inesperado ao consultar as sessões.")
        return

    circuits = {session.circuit_key: session.circuit_name for session in sessions}
    if not circuits:
        st.info(f"A OpenF1 ainda não tem sessões de corrida para {selected_year}.")
        return

    selected_circuit = st.selectbox(
        "Circuito",
        sorted(circuits),
        format_func=lambda key: circuits[key],
    )
    circuit_sessions = tuple(
        session for session in sessions if session.circuit_key == selected_circuit
    )
    try:
        with st.spinner("Buscando e ordenando as voltas do circuito…"):
            fastest_laps = _load_top_five(circuit_sessions, selected_circuit)
    except OpenF1Error as exc:
        LOGGER.error(
            "Falha ao carregar voltas",
            extra={
                "event": "fastest_laps_load_failed",
                "year": selected_year,
                "circuit_key": selected_circuit,
                "error": str(exc),
            },
        )
        st.error(f"Não foi possível carregar as voltas: {exc}")
        return
    except Exception:
        LOGGER.exception(
            "Erro inesperado ao classificar voltas",
            extra={
                "event": "fastest_laps_load_unexpected",
                "year": selected_year,
                "circuit_key": selected_circuit,
            },
        )
        st.error("Ocorreu um erro inesperado ao classificar as voltas.")
        return

    columns = st.columns(3)
    columns[0].metric("Circuito", circuits[selected_circuit])
    columns[1].metric("Sessões de corrida", len(circuit_sessions))
    columns[2].metric("Voltas no top 5", len(fastest_laps))
    st.subheader(f"As voltas mais rápidas · {selected_year}")
    if not fastest_laps:
        st.info("Não há voltas válidas publicadas para esse circuito e temporada.")
        return
    st.dataframe(
        _table_rows(fastest_laps),
        hide_index=True,
        use_container_width=True,
    )
    st.caption(
        "O ranking considera voltas com tempo válido e exclui voltas de saída "
        "dos boxes. "
        "Um piloto pode aparecer mais de uma vez. Fonte: OpenF1."
    )


if __name__ == "__main__":
    main()
