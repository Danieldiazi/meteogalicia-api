"""Tests for MeteoGalicia configuration catalogs."""

import responses

from meteogalicia_api.catalogs import filter_stations, get_concellos
from meteogalicia_api.const import URL_STATIONS
from meteogalicia_api.interface import MeteoGalicia


def test_get_concellos_filters_by_province():
    concellos = get_concellos("A Coruña")

    assert concellos
    assert all(item["provincia"] == "A Coruña" for item in concellos)
    assert {"idConcello": "15078", "concello": "Santiago de Compostela", "provincia": "A Coruña"} in concellos


def test_filter_stations_by_province_and_concello():
    stations = [
        {
            "idEstacion": 10124,
            "estacion": "Santiago-EOAS",
            "provincia": "A Coruña",
            "concello": "Santiago de Compostela",
        },
        {
            "idEstacion": 10045,
            "estacion": "A Coruña",
            "provincia": "A Coruña",
            "concello": "A Coruña",
        },
        {
            "idEstacion": 10050,
            "estacion": "Lugo",
            "provincia": "Lugo",
            "concello": "Lugo",
        },
    ]

    assert filter_stations(
        stations, province="A Coruña", concello="Santiago de Compostela"
    ) == [stations[0]]


@responses.activate
def test_get_stations_uses_authoritative_catalog():
    api = MeteoGalicia()
    responses.add(
        responses.GET,
        URL_STATIONS,
        json={
            "listaEstacionsMeteo": [
                {
                    "idEstacion": 10124,
                    "estacion": "Santiago-EOAS",
                    "provincia": "A Coruña",
                    "concello": "Santiago de Compostela",
                    "lat": 42.887,
                    "lon": -8.531,
                },
                {
                    "idEstacion": 10050,
                    "estacion": "Lugo",
                    "provincia": "Lugo",
                    "concello": "Lugo",
                    "lat": 43.0,
                    "lon": -7.5,
                },
            ]
        },
        status=200,
    )

    stations = api.get_stations(
        province="A Coruña", concello="Santiago de Compostela"
    )

    assert stations is not None
    assert len(stations) == 1
    assert stations[0]["idEstacion"] == 10124
