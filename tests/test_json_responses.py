"""Public JSON methods preserve valid data and handle unavailable responses."""

import pytest
import requests
import responses

from meteogalicia_api.interface import (
    MeteoGalicia,
    URL_FORECAST,
    URL_FORECAST_HOURLY,
    URL_FORECAST_MEDIUM_TERM,
    URL_OBSERVATION,
    URL_OBSERVATION_DAILYDATA_BY_STATION,
    URL_OBSERVATION_LAST10MINDATA_BY_STATION,
)


JSON_ENDPOINTS = [
    pytest.param("get_forecast_data", URL_FORECAST, "15030", id="forecast"),
    pytest.param("get_observation_data", URL_OBSERVATION, "15030", id="observation"),
    pytest.param(
        "get_observation_dailydata_by_station",
        URL_OBSERVATION_DAILYDATA_BY_STATION,
        "10144",
        id="station-daily",
    ),
    pytest.param(
        "get_observation_last10mindata_by_station",
        URL_OBSERVATION_LAST10MINDATA_BY_STATION,
        "10144",
        id="station-last10min",
    ),
    pytest.param(
        "get_hourly_forecast_data", URL_FORECAST_HOURLY, "15030", id="forecast-hourly"
    ),
    pytest.param(
        "get_medium_term_forecast_data",
        URL_FORECAST_MEDIUM_TERM,
        "15030",
        id="forecast-medium-term",
    ),
]


@pytest.mark.parametrize(
    "method,url,identifier,payload",
    [
        pytest.param(
            "get_observation_data",
            URL_OBSERVATION,
            "15030",
            {
                "listaObservacionConcellos": [
                    {"idConcello": 15030, "temperatura": 18.4, "icoEstadoCeo": 201}
                ]
            },
            id="observation",
        ),
        pytest.param(
            "get_observation_dailydata_by_station",
            URL_OBSERVATION_DAILYDATA_BY_STATION,
            "10144",
            {
                "listDatosDiarios": [
                    {"idEstacion": 10144, "data": "2026-01-01", "listaMedidas": []}
                ]
            },
            id="station-daily",
        ),
        pytest.param(
            "get_observation_last10mindata_by_station",
            URL_OBSERVATION_LAST10MINDATA_BY_STATION,
            "10144",
            {
                "listUltimos10min": [
                    {
                        "idEstacion": 10144,
                        "instanteLecturaUTC": "2026-01-01T12:00:00",
                        "listaMedidas": [],
                    }
                ]
            },
            id="station-last10min",
        ),
    ],
)
@responses.activate
def test_valid_observations_are_returned_unchanged(method, url, identifier, payload):
    responses.get(url.format(identifier), json=payload)

    assert getattr(MeteoGalicia(), method)(identifier) == payload


@pytest.mark.parametrize("method,url,identifier", JSON_ENDPOINTS)
@pytest.mark.parametrize("error", [requests.Timeout, requests.ConnectionError])
@responses.activate
def test_network_errors_return_none(method, url, identifier, error):
    responses.get(url.format(identifier), body=error("Simulated network failure"))

    assert getattr(MeteoGalicia(), method)(identifier) is None


@pytest.mark.parametrize("method,url,identifier", JSON_ENDPOINTS)
@pytest.mark.parametrize("status", [429, 503])
@responses.activate
def test_http_errors_return_none(method, url, identifier, status):
    responses.get(url.format(identifier), status=status, json={"error": "Unavailable"})

    assert getattr(MeteoGalicia(), method)(identifier) is None


@pytest.mark.parametrize("method,url,identifier", JSON_ENDPOINTS)
@pytest.mark.parametrize(
    "body", ["", '{"incomplete":'], ids=["empty-body", "invalid-json"]
)
@responses.activate
def test_invalid_json_returns_none(method, url, identifier, body):
    responses.get(url.format(identifier), body=body, content_type="application/json")

    assert getattr(MeteoGalicia(), method)(identifier) is None


@pytest.mark.parametrize(
    "method,url,identifier",
    [
        pytest.param(
            "get_forecast_data", URL_FORECAST, "15030", id="forecast",
            marks=pytest.mark.xfail(
                strict=True, raises=KeyError,
                reason="Known limitation: get_forecast_data indexes missing predConcello",
            ),
        ),
        pytest.param(
            "get_observation_data", URL_OBSERVATION, "15030", id="observation",
            marks=pytest.mark.xfail(
                strict=True, raises=KeyError,
                reason="Known limitation: get_observation_data indexes missing listaObservacionConcellos",
            ),
        ),
        JSON_ENDPOINTS[2],
        JSON_ENDPOINTS[3],
    ],
)
@responses.activate
def test_missing_payload_key_returns_none(method, url, identifier):
    responses.get(url.format(identifier), json={})

    assert getattr(MeteoGalicia(), method)(identifier) is None


@pytest.mark.parametrize(
    "method,url,identifier,key",
    [
        (
            "get_observation_data", URL_OBSERVATION,
            "15030", "listaObservacionConcellos",
        ),
        (
            "get_observation_dailydata_by_station",
            URL_OBSERVATION_DAILYDATA_BY_STATION, "10144", "listDatosDiarios",
        ),
        (
            "get_observation_last10mindata_by_station",
            URL_OBSERVATION_LAST10MINDATA_BY_STATION, "10144", "listUltimos10min",
        ),
    ],
    ids=["observation", "station-daily", "station-last10min"],
)
@pytest.mark.xfail(
    strict=True,
    raises=TypeError,
    reason="Known limitation: observation methods call len() on a null list",
)
@responses.activate
def test_null_observation_list_returns_none(method, url, identifier, key):
    responses.get(url.format(identifier), json={key: None})

    assert getattr(MeteoGalicia(), method)(identifier) is None
