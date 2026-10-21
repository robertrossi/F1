import httpx
import pytest

from f1 import OpenF1Client, Settings
from f1.api.client import OpenF1ConnectionError, OpenF1Error, OpenF1HTTPError


def client_for(handler):
    transport = httpx.MockTransport(handler)
    return OpenF1Client(
        Settings(base_url="https://test.local/v1"),
        http_client=httpx.Client(transport=transport),
    )


def test_query_filters_are_encoded_and_repeated():
    def handler(request):
        assert request.url.path == "/v1/drivers"
        assert request.url.params.get_list("driver_number") == ["1", "44"]
        assert request.url.params["date>="] == "2025-01-01T00:00:00Z"
        return httpx.Response(200, json=[{"driver_number": 1, "team_colour": None}])

    assert client_for(handler).get_drivers(
        driver_number=[1, 44], **{"date>=": "2025-01-01T00:00:00Z"}
    ) == [{"driver_number": 1, "team_colour": None}]


def test_endpoints_and_json_records():
    seen = []

    def handler(request):
        seen.append(request.url.path)
        return httpx.Response(200, json=[])

    client = client_for(handler)
    assert client.get_meetings(year=2025) == []
    assert client.get_sessions(year=2025) == []
    assert client.get_drivers(session_key="latest") == []
    assert client.get_laps(session_key="latest") == []
    assert seen == ["/v1/meetings", "/v1/sessions", "/v1/drivers", "/v1/laps"]


def test_http_errors_are_clear():
    client = client_for(lambda request: httpx.Response(404))
    with pytest.raises(OpenF1HTTPError, match="HTTP 404"):
        client.get("meetings")


def test_rate_limit_retries_once_when_retry_after_is_zero():
    responses = [
        httpx.Response(429, headers={"Retry-After": "0"}),
        httpx.Response(200, json=[]),
    ]
    client = client_for(lambda request: responses.pop(0))

    assert client.get("meetings") == []


def test_rate_limit_stops_after_bounded_retries():
    calls = 0

    def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(429, headers={"Retry-After": "0"})

    client = client_for(handler)
    with pytest.raises(OpenF1HTTPError, match="HTTP 429"):
        client.get("meetings")
    assert calls == 3


def test_connection_errors_are_wrapped():
    def handler(request):
        raise httpx.ConnectError("offline", request=request)

    with pytest.raises(OpenF1ConnectionError, match="Falha de conexão"):
        client_for(handler).get("sessions")


def test_timeout_errors_are_wrapped():
    def handler(request):
        raise httpx.ReadTimeout("slow", request=request)

    with pytest.raises(OpenF1ConnectionError, match="Timeout"):
        client_for(handler).get("sessions")


@pytest.mark.parametrize("payload", [{"unexpected": True}, [None]])
def test_unexpected_payloads_raise_domain_error(payload):
    with pytest.raises(OpenF1Error, match="Formato inesperado"):
        client_for(lambda request: httpx.Response(200, json=payload)).get("meetings")


def test_invalid_endpoint_and_settings():
    with pytest.raises(ValueError):
        client_for(lambda request: httpx.Response(200, json=[])).get("../secret")
    with pytest.raises(ValueError):
        Settings(timeout=0)


def test_invalid_json_response_raises_domain_error():
    response = httpx.Response(200, text="not json")
    client = client_for(lambda request: response)
    with pytest.raises(OpenF1Error, match="Resposta inválida"):
        client.get("meetings")


def test_retry_after_invalid_value_uses_backoff(monkeypatch):
    delays = []
    monkeypatch.setattr("f1.api.client.time.sleep", delays.append)
    responses = [
        httpx.Response(429, headers={"Retry-After": "later"}),
        httpx.Response(200, json=[]),
    ]
    assert client_for(lambda request: responses.pop(0)).get("meetings") == []
    assert delays == [0.5]


def test_retry_after_is_capped(monkeypatch):
    delays = []
    monkeypatch.setattr("f1.api.client.time.sleep", delays.append)
    responses = [
        httpx.Response(429, headers={"Retry-After": "20"}),
        httpx.Response(200, json=[]),
    ]
    assert client_for(lambda request: responses.pop(0)).get("meetings") == []
    assert delays == [5.0]


def test_close_only_closes_owned_http_client(monkeypatch):
    injected = client_for(lambda request: httpx.Response(200, json=[]))
    injected_transport = injected._client
    injected.close()
    assert not injected_transport.is_closed
    injected_transport.close()

    class FakeClient:
        is_closed = False

        def close(self):
            self.is_closed = True

    owned_transport = FakeClient()
    monkeypatch.setattr("f1.api.client.httpx.Client", lambda **kwargs: owned_transport)
    owned = OpenF1Client()
    owned.close()
    assert owned_transport.is_closed
