"""Typed errors must preserve the legacy None-returning API contract."""

from datetime import datetime, timezone

import pytest
import requests
import responses

from meteogalicia_api.const import URL_FORECAST, URL_OBSERVATION
from meteogalicia_api.errors import (
    MeteoGaliciaConnectionError,
    MeteoGaliciaHTTPError,
    MeteoGaliciaInvalidResponseError,
    MeteoGaliciaNoDataError,
    MeteoGaliciaTimeoutError,
    retry_after_seconds,
)
from meteogalicia_api.interface import MeteoGalicia


@pytest.mark.parametrize("strict", [False, True])
@pytest.mark.parametrize("status,retryable", [(400, False), (404, False), (429, True), (503, True)])
@responses.activate
def test_http_errors_preserve_status_and_retry_policy(strict, status, retryable):
    client = MeteoGalicia(raise_on_error=strict)
    responses.get(URL_FORECAST.format("15030"), status=status, headers={"Retry-After": "120"})
    if strict:
        with pytest.raises(MeteoGaliciaHTTPError):
            client.get_forecast_data("15030")
    else:
        assert client.get_forecast_data("15030") is None
    assert client.last_error.status_code == status
    assert client.last_error.retryable is retryable
    assert client.last_error.retry_after == (120 if retryable else None)


@pytest.mark.parametrize("strict", [False, True])
@pytest.mark.parametrize("exception,error_type", [
    (requests.exceptions.Timeout(), MeteoGaliciaTimeoutError),
    (requests.exceptions.ConnectionError(), MeteoGaliciaConnectionError),
])
@responses.activate
def test_transport_errors_remain_distinguishable(strict, exception, error_type):
    client = MeteoGalicia(raise_on_error=strict)
    responses.get(URL_FORECAST.format("15030"), body=exception)
    if strict:
        with pytest.raises(error_type):
            client.get_forecast_data("15030")
    else:
        assert client.get_forecast_data("15030") is None
    assert isinstance(client.last_error, error_type)
    assert client.last_error.retryable


@pytest.mark.parametrize("payload", [None, [], "text", 2, {"predConcello": []}])
@responses.activate
def test_invalid_json_structures_raise_only_when_requested(payload):
    client = MeteoGalicia(raise_on_error=True)
    responses.get(URL_FORECAST.format("15030"), json=payload)
    with pytest.raises(MeteoGaliciaInvalidResponseError):
        client.get_forecast_data("15030")
    assert not client.last_error.retryable


@responses.activate
def test_empty_observations_are_not_reported_as_invalid_json():
    client = MeteoGalicia(raise_on_error=True)
    responses.get(URL_OBSERVATION.format("15030"), json={"listaObservacionConcellos": []})
    with pytest.raises(MeteoGaliciaNoDataError):
        client.get_observation_data("15030")


@pytest.mark.parametrize("xml", [False, True])
@responses.activate
def test_invalid_documents_use_response_error_category(xml):
    client = MeteoGalicia(raise_on_error=True)
    responses.get("https://example.com/forecast", body="not a document")
    with pytest.raises(MeteoGaliciaInvalidResponseError):
        if xml:
            client._do_getGeoRSS("https://example.com/forecast", "1", "today", "tomorrow")
        else:
            client._do_get("https://example.com/forecast")


@responses.activate
def test_success_clears_a_previous_error():
    client = MeteoGalicia()
    responses.get(URL_FORECAST.format("15030"), status=500)
    responses.get(URL_FORECAST.format("15030"), json={"predConcello": {"id": "15030"}})
    assert client.get_forecast_data("15030") is None
    assert client.last_error is not None
    assert client.get_forecast_data("15030") == {"predConcello": {"id": "15030"}}
    assert client.last_error is None


@pytest.mark.parametrize("header,expected", [("30", 30), ("0", 0), ("nan", None), ("inf", None), ("-1", None), ("bad", None), (None, None)])
def test_retry_after_seconds(header, expected):
    assert retry_after_seconds(header) == expected


def test_retry_after_http_date_and_expired_deadline():
    now = datetime(2026, 10, 10, 12, tzinfo=timezone.utc)
    assert retry_after_seconds("Sat, 10 Oct 2026 12:02:00 GMT", now) == 120
    assert retry_after_seconds("Sat, 10 Oct 2026 11:59:00 GMT", now) == 0
