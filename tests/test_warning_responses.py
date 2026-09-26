"""Municipal warning responses, including snapshots from the public service."""

import json
from pathlib import Path

import pytest
import responses

from meteogalicia_api.interface import (
    MeteoGalicia,
    URL_MAX_WARNING_LEVELS,
    URL_WARNINGS,
)


ENDPOINTS = [
    ("get_warnings_data", URL_WARNINGS, "listaAvisosConcellos", "warnings"),
    ("get_max_warning_levels_data", URL_MAX_WARNING_LEVELS, "listaNiveisMaximos", "warning_levels"),
]


@pytest.mark.parametrize("method,url,key,fixture", ENDPOINTS)
@pytest.mark.parametrize("day,suffix", [(-1, "all_days"), (1, "tomorrow")])
@responses.activate
def test_real_responses_are_returned_unchanged(method, url, key, fixture, day, suffix):
    payload = json.loads(
        (Path(__file__).parent / "fixtures" / f"{fixture}_{suffix}.json").read_text(encoding="utf-8")
    )
    responses.get(url.format("15030", day), json=payload)

    assert getattr(MeteoGalicia(), method)("15030", day=day) == payload


@pytest.mark.parametrize("method,url,key,fixture", ENDPOINTS)
@responses.activate
def test_empty_daily_lists_are_valid(method, url, key, fixture):
    payload = {"listaDiaConcellos": [{"dia": 0, key: []}]}
    responses.get(url.format("15030", 0), json=payload)

    assert getattr(MeteoGalicia(), method)("15030", day=0) == payload


@responses.activate
def test_warning_details_and_unknown_fields_are_preserved():
    warning = {
        "idConcello": 15030,
        "idNivel": 2,
        "dataIni": "2026-09-27T06:00:00",
        "dataFin": "2026-09-27T18:00:00",
        "tipoalerta_es": "Viento",
        "future_field": {"keep": True},
    }
    payload = {"listaDiaConcellos": [{"dia": 1, "listaAvisosConcellos": [warning]}]}
    responses.get(URL_WARNINGS.format("15030", -1), json=payload)

    assert MeteoGalicia().get_warnings_data("15030") == payload


@pytest.mark.parametrize("method,url,key,fixture", ENDPOINTS)
@pytest.mark.parametrize(
    "payload",
    [None, {}, [], {"listaDiaConcellos": None}, {"listaDiaConcellos": {}},
     {"listaDiaConcellos": [None]}, {"listaDiaConcellos": [{"dia": 0}]},
     {"listaDiaConcellos": [{"dia": 0, "wrong": []}]}],
)
@responses.activate
def test_warning_methods_reject_invalid_payloads(method, url, key, fixture, payload):
    responses.get(url.format("15030", -1), json=payload)

    assert getattr(MeteoGalicia(), method)("15030") is None


@pytest.mark.parametrize("method,url,key,fixture", ENDPOINTS)
@pytest.mark.parametrize("items", [None, {}, "invalid"])
@responses.activate
def test_invalid_daily_list_is_rejected_even_after_a_valid_day(method, url, key, fixture, items):
    payload = {"listaDiaConcellos": [{"dia": 0, key: []}, {"dia": 1, key: items}]}
    responses.get(url.format("15030", -1), json=payload)

    assert getattr(MeteoGalicia(), method)("15030") is None


@pytest.mark.parametrize("method,url,key,fixture", ENDPOINTS)
@responses.activate
def test_warning_methods_return_none_on_http_error(method, url, key, fixture):
    responses.get(url.format("15030", -1), status=500)

    assert getattr(MeteoGalicia(), method)("15030") is None
