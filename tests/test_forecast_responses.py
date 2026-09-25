"""Hourly forecast responses, based on real payloads (trimmed)."""

import pytest
import responses

from meteogalicia_api.interface import MeteoGalicia, URL_FORECAST_HOURLY


HOURLY_PAYLOAD = {
    "predHoraria": {
        "idConcello": 15030,
        "nome": "A Coruña",
        "listaPredDiaHoraria": [
            {
                "dia": 0,
                "listaPredHora": [
                    {
                        "dataPredicion": "2026-09-26T00:00:00",
                        "icoCeo": 201,
                        "icoVento": 302,
                        "tMedia": 17,
                    },
                    {
                        "dataPredicion": "2026-09-26T01:00:00",
                        "icoCeo": 203,
                        "icoVento": 302,
                        "tMedia": 15,
                    },
                ],
            }
        ],
    }
}

# What MeteoGalicia returns (HTTP 200) for a code that does not exist.
HOURLY_UNKNOWN_CODE = {
    "predHoraria": {"idConcello": 0, "listaPredDiaHoraria": [], "nome": None}
}


@responses.activate
def test_hourly_forecast_is_returned_unchanged():
    responses.get(URL_FORECAST_HOURLY.format("15030"), json=HOURLY_PAYLOAD)

    assert MeteoGalicia().get_hourly_forecast_data("15030") == HOURLY_PAYLOAD


@pytest.mark.parametrize(
    "payload",
    [
        HOURLY_UNKNOWN_CODE,
        {"predHoraria": None},
        {"predHoraria": {"idConcello": 15030, "listaPredDiaHoraria": None}},
        {},
        [],
    ],
    ids=["unknown-code", "null-prediction", "null-list", "missing-key", "not-a-dict"],
)
@responses.activate
def test_hourly_forecast_without_data_returns_none(payload):
    responses.get(URL_FORECAST_HOURLY.format("99999"), json=payload)

    assert MeteoGalicia().get_hourly_forecast_data("99999") is None
