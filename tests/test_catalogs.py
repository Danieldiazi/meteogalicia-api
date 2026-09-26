"""Tests for MeteoGalicia configuration catalogs."""

import responses

from meteogalicia_api.catalogs import (
    filter_stations,
    get_concellos,
    sort_stations_by_distance,
)
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


def test_sort_stations_by_distance_adds_distance_and_orders():
    stations = [
        {
            "idEstacion": 1,
            "estacion": "Far",
            "lat": 43.5,
            "lon": -8.5,
        },
        {
            "idEstacion": 2,
            "estacion": "Near",
            "lat": 43.36,
            "lon": -8.41,
        },
        {
            "idEstacion": 3,
            "estacion": "Without coordinates",
        },
    ]

    ranked = sort_stations_by_distance(stations, 43.3623, -8.4115)

    assert [item["idEstacion"] for item in ranked] == [2, 1]
    assert ranked[0]["distance_km"] < ranked[1]["distance_km"]
    assert "distance_km" not in stations[0]


def test_get_nearest_stations_filters_and_orders():
    payload = {
        "listaEstacionsMeteo": [
            {
                "idEstacion": 10124,
                "estacion": "Santiago-EOAS",
                "provincia": "A Coruña",
                "concello": "Santiago de Compostela",
                "lat": 42.8782,
                "lon": -8.5448,
            },
            {
                "idEstacion": 10125,
                "estacion": "Santiago-Campus",
                "provincia": "A Coruña",
                "concello": "Santiago de Compostela",
                "lat": 42.8748,
                "lon": -8.5580,
            },
            {
                "idEstacion": 10045,
                "estacion": "A Coruña",
                "provincia": "A Coruña",
                "concello": "A Coruña",
                "lat": 43.3623,
                "lon": -8.4115,
            },
        ]
    }

    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, URL_STATIONS, json=payload, status=200)
        ranked = MeteoGalicia().get_nearest_stations(
            42.8780,
            -8.5450,
            province="A Coruña",
            concello="Santiago de Compostela",
        )

    assert ranked is not None
    assert [item["idEstacion"] for item in ranked] == [10124, 10125]
    assert all("distance_km" in item for item in ranked)
