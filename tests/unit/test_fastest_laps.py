from __future__ import annotations

from typing import Any

import pytest

from f1.services.fastest_laps import FastestLapService, RaceSession, format_lap_time


class FakeOpenF1:
    def __init__(self) -> None:
        self.meetings = [
            {
                "meeting_key": 1,
                "meeting_name": "Grand Prix A",
                "circuit_key": 10,
                "circuit_short_name": "Circuit A",
            },
            {
                "meeting_key": 2,
                "meeting_name": "Grand Prix B",
                "circuit_key": 10,
                "circuit_short_name": "Circuit A",
            },
            {
                "meeting_key": 3,
                "meeting_name": "Grand Prix C",
                "circuit_key": 20,
                "circuit_short_name": "Circuit C",
            },
        ]
        self.sessions_by_meeting = {
            1: [
                {"session_key": 101, "session_type": "Practice"},
                {"session_key": 102, "session_type": "Race"},
            ],
            2: [{"session_key": 201, "session_type": "Race"}],
            3: [{"session_key": 301, "session_type": "Race"}],
        }
        self.laps_by_session: dict[int, list[dict[str, Any]]] = {
            102: [
                {"driver_number": 44, "lap_number": 12, "lap_duration": 90.5},
                {"driver_number": 1, "lap_number": 8, "lap_duration": 89.9},
                {"driver_number": 16, "lap_number": 6, "lap_duration": 88.8},
                {"driver_number": 77, "lap_number": 3, "lap_duration": 91.2},
                {"driver_number": 11, "lap_number": 9, "lap_duration": 87.5},
                {"driver_number": 55, "lap_number": 4, "lap_duration": 88.0},
                {
                    "driver_number": 63,
                    "lap_number": 2,
                    "lap_duration": 80.0,
                    "is_pit_out_lap": True,
                },
                {"driver_number": 31, "lap_number": 2, "lap_duration": None},
                {"driver_number": 14, "lap_number": 2, "lap_duration": "88.2"},
                {"driver_number": 44, "lap_number": 1, "lap_duration": -1},
            ],
            201: [
                {"driver_number": 4, "lap_number": 18, "lap_duration": 87.8},
                {"driver_number": 81, "lap_number": 20, "lap_duration": 89.0},
            ],
            301: [{"driver_number": 1, "lap_number": 4, "lap_duration": 80.0}],
        }
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def get_meetings(self, **filters: Any) -> list[dict[str, Any]]:
        self.calls.append(("meetings", filters))
        return self.meetings

    def get_sessions(self, **filters: Any) -> list[dict[str, Any]]:
        self.calls.append(("sessions", filters))
        if "year" in filters:
            return [
                dict(session, meeting_key=meeting_key)
                for meeting_key, sessions in self.sessions_by_meeting.items()
                for session in sessions
            ]
        return self.sessions_by_meeting[filters["meeting_key"]]

    def get_drivers(self, **filters: Any) -> list[dict[str, Any]]:
        self.calls.append(("drivers", filters))
        return [
            {
                "driver_number": number,
                "full_name": f"Driver {number}",
                "team_name": f"Team {number}",
            }
            for number in (1, 4, 11, 16, 44, 55, 77, 81)
        ]

    def get_laps(self, **filters: Any) -> list[dict[str, Any]]:
        self.calls.append(("laps", filters))
        return self.laps_by_session.get(int(filters["session_key"]), [])


def test_race_session_listing_excludes_practice_and_groups_circuits() -> None:
    api = FakeOpenF1()

    sessions = FastestLapService(api).race_sessions_for_year(2025)

    assert [session.session_key for session in sessions] == ["102", "201", "301"]
    assert sessions[0].circuit_key == sessions[1].circuit_key == "10"
    assert api.calls[0] == ("meetings", {"year": 2025})


def test_fastest_laps_returns_top_five_for_selected_circuit_only() -> None:
    api = FakeOpenF1()
    service = FastestLapService(api)
    sessions = service.race_sessions_for_year(2025)

    fastest = service.fastest_laps(sessions, "10")

    assert [lap.lap_duration for lap in fastest] == [87.5, 87.8, 88.0, 88.8, 89.0]
    assert [lap.driver_number for lap in fastest] == ["11", "4", "55", "16", "81"]
    assert fastest[0].driver_name == "Driver 11"
    assert fastest[0].meeting_name == "Grand Prix A"
    assert all(lap.circuit_key == "10" for lap in fastest)
    lap_calls = [filters for name, filters in api.calls if name == "laps"]
    assert lap_calls == [
        {"session_key": "102", "is_pit_out_lap": False},
        {"session_key": "201", "is_pit_out_lap": False},
    ]


def test_fastest_laps_handles_missing_drivers_and_limits_results() -> None:
    api = FakeOpenF1()
    sessions = (RaceSession("10", "Circuit A", "1", "Grand Prix A", "102"),)
    api.laps_by_session[102] = [
        {"driver_number": 99, "lap_number": 5, "lap_duration": 88.0}
    ]

    fastest = FastestLapService(api).fastest_laps(sessions, "10")

    assert fastest[0].driver_name == "Piloto 99"
    assert fastest[0].team_name == "—"


def test_fastest_laps_rejects_non_positive_limit() -> None:
    with pytest.raises(ValueError, match="limit"):
        FastestLapService(FakeOpenF1()).fastest_laps((), "10", limit=0)


def test_format_lap_time_and_invalid_values() -> None:
    assert format_lap_time(91.743) == "1:31.743"
    assert format_lap_time(59.9) == "0:59.900"
    with pytest.raises(ValueError, match="finito"):
        format_lap_time(float("nan"))
    with pytest.raises(ValueError, match="finito"):
        format_lap_time(-1)
