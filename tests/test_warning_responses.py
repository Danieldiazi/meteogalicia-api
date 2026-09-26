"""Municipal warning endpoint responses."""

import pytest
import responses

from meteogalicia_api.interface import (
    MeteoGalicia,
    URL_MAX_WARNING_LEVELS,
    URL_WARNINGS,
)


WARNINGS_PAYLOAD = {
    "dia": 0,
    "listaAvisosConcellos": [
        {
            "idconcello": 15030,
            "nomeConcello": "A Coruña",
            "idNivel": 2,
            "dataAviso": "2026-09-26T12:00:00",
            "dataIni": "2026-09-27T06:00:00",
            "dataFin": "2026-09-27T18:00:00",
            "idTipoAlerta": 1,
            "tipoalerta_gl": "Vento",
            "tipoalerta_es": "Viento",
        }
    ],
}

MAX_LEVELS_PAYLOAD = {
    "dia": -1,
    "listaNiveisMaximos": [
        {"idconcello": 15030, "nomeConcello": "A Coruña", "nivelMax": 0},
        {"idconcello": 15030, "nomeConcello": "A Coruña", "nivelMax": 2},
        {"idconcello": 15030, "nomeConcello": "A Coruña", "nivelMax": 1},
    ],
}


@responses.activate
def test_warnings_are_returned_unchanged():
    responses.get(URL_WARNINGS.format("15030", -1), json=WARNINGS_PAYLOAD)

    assert MeteoGalicia().get_warnings_data("15030") == WARNINGS_PAYLOAD


@responses.activate
def test_warnings_support_explicit_day():
    responses.get(URL_WARNINGS.format("15030", 1), json=WARNINGS_PAYLOAD)

    assert MeteoGalicia().get_warnings_data("15030", day=1) == WARNINGS_PAYLOAD


@responses.activate
def test_empty_warning_list_is_valid():
    payload = {"dia": 0, "listaAvisosConcellos": []}
    responses.get(URL_WARNINGS.format("15030", 0), json=payload)

    assert MeteoGalicia().get_warnings_data("15030", day=0) == payload


@responses.activate
def test_max_warning_levels_are_returned_unchanged():
    responses.get(URL_MAX_WARNING_LEVELS.format("15030", -1), json=MAX_LEVELS_PAYLOAD)

    assert MeteoGalicia().get_max_warning_levels_data("15030") == MAX_LEVELS_PAYLOAD


@responses.activate
def test_empty_max_warning_level_list_is_valid():
    payload = {"dia": -1, "listaNiveisMaximos": []}
    responses.get(URL_MAX_WARNING_LEVELS.format("15030", -1), json=payload)

    assert MeteoGalicia().get_max_warning_levels_data("15030") == payload


@pytest.mark.parametrize(
    "method,url,key",
    [
        ("get_warnings_data", URL_WARNINGS, "listaAvisosConcellos"),
        ("get_max_warning_levels_data", URL_MAX_WARNING_LEVELS, "listaNiveisMaximos"),
    ],
)
@pytest.mark.parametrize(
    "payload",
    [
        {},
        [],
        {"wrong": []},
        {"value": None},
    ],
)
@responses.activate
def test_warning_methods_reject_invalid_payloads(method, url, key, payload):
    if isinstance(payload, dict) and "value" in payload:
        payload = {key: payload["value"]}
    responses.get(url.format("15030", -1), json=payload)

    assert getattr(MeteoGalicia(), method)("15030") is None


@pytest.mark.parametrize(
    "method,url",
    [
        ("get_warnings_data", URL_WARNINGS),
        ("get_max_warning_levels_data", URL_MAX_WARNING_LEVELS),
    ],
)
@responses.activate
def test_warning_methods_return_none_on_http_error(method, url):
    responses.get(url.format("15030", -1), status=500)

    assert getattr(MeteoGalicia(), method)("15030") is None
