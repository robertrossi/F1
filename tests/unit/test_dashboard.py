from contextlib import nullcontext
from unittest.mock import Mock

import f1.dashboard as dashboard
from f1.api.client import OpenF1Error
from f1.services.fastest_laps import FastestLap, RaceSession


class FakeStreamlit:
    def __init__(self, sessions):
        self.sessions = sessions
        self.messages = []
        self.data = None

    def __getattr__(self, name):
        if name in {"set_page_config", "title", "caption", "subheader"}:
            return lambda *args, **kwargs: None
        if name == "selectbox":
            return self.selectbox
        if name == "spinner":
            return lambda *args, **kwargs: nullcontext()
        if name == "columns":
            return lambda count: [Mock() for _ in range(count)]
        if name == "dataframe":
            return self.save_data
        if name in {"info", "error"}:
            return self.messages.append
        raise AttributeError(name)

    def selectbox(self, label, options, **kwargs):
        if label == "Temporada":
            return 2025
        return options[0]

    def save_data(self, data, **kwargs):
        self.data = data


def test_table_rows_include_ranked_lap_data():
    lap = FastestLap(
        circuit_key="10",
        circuit_name="Circuit A",
        meeting_name="Grand Prix A",
        session_key="102",
        driver_number="44",
        driver_name="Driver 44",
        team_name="Team A",
        lap_number=12,
        lap_duration=91.743,
    )

    rows = dashboard._table_rows((lap,))

    assert rows == [
        {
            "Posição": 1,
            "Piloto": "Driver 44 (#44)",
            "Equipe": "Team A",
            "Tempo": "1:31.743",
            "Grande Prêmio": "Grand Prix A",
            "Volta": 12,
        }
    ]


def test_main_renders_season_circuit_and_top_five(monkeypatch):
    session = RaceSession("10", "Circuit A", "1", "Grand Prix A", "102")
    lap = FastestLap(
        "10",
        "Circuit A",
        "Grand Prix A",
        "102",
        "44",
        "Driver 44",
        "Team A",
        12,
        91.743,
    )
    fake_st = FakeStreamlit((session,))
    monkeypatch.setattr(dashboard, "st", fake_st)
    monkeypatch.setattr(dashboard, "configure_logging", lambda: None)
    sessions_loader = Mock(return_value=(session,))
    laps_loader = Mock(return_value=(lap,))
    monkeypatch.setattr(dashboard, "_load_race_sessions", sessions_loader)
    monkeypatch.setattr(dashboard, "_load_top_five", laps_loader)

    dashboard.main()

    sessions_loader.assert_called_once_with(2025)
    laps_loader.assert_called_once_with((session,), "10")
    assert fake_st.data[0]["Piloto"] == "Driver 44 (#44)"
    assert not fake_st.messages


def test_main_shows_empty_state_without_race_sessions(monkeypatch):
    fake_st = FakeStreamlit(())
    monkeypatch.setattr(dashboard, "st", fake_st)
    monkeypatch.setattr(dashboard, "configure_logging", lambda: None)
    monkeypatch.setattr(dashboard, "_load_race_sessions", Mock(return_value=()))

    dashboard.main()

    assert fake_st.messages == ["A OpenF1 ainda não tem sessões de corrida para 2025."]


def test_main_reports_session_loading_errors(monkeypatch):
    fake_st = FakeStreamlit(())
    monkeypatch.setattr(dashboard, "st", fake_st)
    monkeypatch.setattr(dashboard, "configure_logging", lambda: None)
    monkeypatch.setattr(
        dashboard, "_load_race_sessions", Mock(side_effect=OpenF1Error("offline"))
    )
    dashboard.main()
    assert fake_st.messages == ["Não foi possível carregar as sessões: offline"]


def test_main_reports_unexpected_session_loading_errors(monkeypatch):
    fake_st = FakeStreamlit(())
    monkeypatch.setattr(dashboard, "st", fake_st)
    monkeypatch.setattr(dashboard, "configure_logging", lambda: None)
    monkeypatch.setattr(
        dashboard, "_load_race_sessions", Mock(side_effect=RuntimeError("broken"))
    )
    dashboard.main()
    assert fake_st.messages == ["Ocorreu um erro inesperado ao consultar as sessões."]


def test_main_reports_lap_loading_errors(monkeypatch):
    session = RaceSession("10", "Circuit A", "1", "Grand Prix A", "102")
    fake_st = FakeStreamlit((session,))
    monkeypatch.setattr(dashboard, "st", fake_st)
    monkeypatch.setattr(dashboard, "configure_logging", lambda: None)
    monkeypatch.setattr(dashboard, "_load_race_sessions", Mock(return_value=(session,)))
    monkeypatch.setattr(
        dashboard, "_load_top_five", Mock(side_effect=OpenF1Error("offline"))
    )
    dashboard.main()
    assert fake_st.messages == ["Não foi possível carregar as voltas: offline"]


def test_main_reports_unexpected_lap_errors(monkeypatch):
    session = RaceSession("10", "Circuit A", "1", "Grand Prix A", "102")
    fake_st = FakeStreamlit((session,))
    monkeypatch.setattr(dashboard, "st", fake_st)
    monkeypatch.setattr(dashboard, "configure_logging", lambda: None)
    monkeypatch.setattr(dashboard, "_load_race_sessions", Mock(return_value=(session,)))
    monkeypatch.setattr(
        dashboard, "_load_top_five", Mock(side_effect=RuntimeError("broken"))
    )
    dashboard.main()
    assert fake_st.messages == ["Ocorreu um erro inesperado ao classificar as voltas."]


def test_main_shows_empty_ranking_without_dataframe(monkeypatch):
    session = RaceSession("10", "Circuit A", "1", "Grand Prix A", "102")
    fake_st = FakeStreamlit((session,))
    monkeypatch.setattr(dashboard, "st", fake_st)
    monkeypatch.setattr(dashboard, "configure_logging", lambda: None)
    monkeypatch.setattr(dashboard, "_load_race_sessions", Mock(return_value=(session,)))
    monkeypatch.setattr(dashboard, "_load_top_five", Mock(return_value=()))
    dashboard.main()
    assert fake_st.messages == [
        "Não há voltas válidas publicadas para esse circuito e temporada."
    ]
    assert fake_st.data is None
