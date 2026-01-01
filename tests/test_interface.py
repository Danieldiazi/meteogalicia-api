import responses

from meteogalicia_api.interface import MeteoGalicia, URL_FORECAST, URL_OBSERVATION


@responses.activate
def test_get_forecast_data_ok():
    api = MeteoGalicia()
    responses.add(
        responses.GET,
        URL_FORECAST.format("15030"),
        json={"predConcello": {"id": "15030"}},
        status=200,
    )

    data = api.get_forecast_data("15030")
    assert data["predConcello"]["id"] == "15030"


@responses.activate
def test_get_forecast_data_http_error():
    api = MeteoGalicia()
    responses.add(
        responses.GET,
        URL_FORECAST.format("15030"),
        json={"error": "fail"},
        status=500,
    )

    data = api.get_forecast_data("15030")
    assert data is None


@responses.activate
def test_get_observation_data_empty_list():
    api = MeteoGalicia()
    responses.add(
        responses.GET,
        URL_OBSERVATION.format("15030"),
        json={"listaObservacionConcellos": []},
        status=200,
    )

    data = api.get_observation_data("15030")
    assert data["listaObservacionConcellos"] == []
