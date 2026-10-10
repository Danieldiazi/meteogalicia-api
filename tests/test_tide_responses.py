"""Tide requests and parsing with deterministic dates and compact RSS fixtures."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
import requests
import responses

from meteogalicia_api import interface
from meteogalicia_api.interface import MeteoGalicia, URL_FORECAST_TIDE


@pytest.fixture
def tide_url(monkeypatch):
    """Keep the requested window stable, including the year boundary."""

    class FrozenDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 1, 1, 12, tzinfo=tz)

    monkeypatch.setattr(interface, "datetime", FrozenDateTime)
    return URL_FORECAST_TIDE.format("3", "31/12/2025", "02/01/2026")


def _item(day, hour, *, include_tides=True, include_port=True):
    tides = ""
    if include_tides:
        tides = (
            f'<Mareas:mareas estado="Preamar" hora="{hour}:10" altura="3,2" />'
            f'<Mareas:mareas estado="Baixamar" hora="{hour}:40" altura="1,1" />'
        )
    port = (
        '<Mareas:idPorto descricion="IdPorto">3</Mareas:idPorto>'
        if include_port else ""
    )
    return (
        f'<item><dc:date>{day:%Y-%m-%d}T00:00:00Z</dc:date>'
        '<georss:point>42.23 -8.71</georss:point>'
        f'{port}<Mareas:nomePorto descricion="Porto">Vigo</Mareas:nomePorto>'
        f'<Mareas:dataPredicion formato="dd/MM/yyyy">{day:%d/%m/%Y}</Mareas:dataPredicion>'
        f'{tides}</item>'
    )


def _rss(items):
    return (
        '<rss xmlns:dc="http://purl.org/dc/elements/1.1/" '
        'xmlns:georss="http://www.georss.org/georss" xmlns:Mareas="Mareas">'
        f'<channel>{"".join(items)}</channel></rss>'
    )


@pytest.fixture
def tide_items():
    return [
        _item(datetime(2025, 12, 31), "01"),
        _item(datetime(2026, 1, 1), "02"),
        _item(datetime(2026, 1, 2), "03"),
    ]


@responses.activate
def test_tide_output_preserves_the_existing_contract(tide_url, tide_items):
    responses.get(tide_url, body=_rss(tide_items), content_type="application/xml")

    assert MeteoGalicia().get_forecast_tide("3") == {
        "pointGeoRSS": "42.23 -8.71",
        "date": "2026-01-01T00:00:00Z",
        "yesterdayDate": "2025-12-31",
        "todayDate": "2026-01-01",
        "tomorrowDate": "2026-01-02",
        "portId": "3",
        "portName": "Vigo",
        "yesterdayLastTide": {
            "@estado": "Baixamar", "@hora": "01:40", "@altura": "1,1"
        },
        "todayTides": [
            {"@estado": "Preamar", "@hora": "02:10", "@altura": "3,2"},
            {"@estado": "Baixamar", "@hora": "02:40", "@altura": "1,1"},
        ],
        "tomorrowFirstTide": {
            "@estado": "Preamar", "@hora": "03:10", "@altura": "3,2"
        },
        "tomorrowTides": [
            {"@estado": "Preamar", "@hora": "03:10", "@altura": "3,2"},
            {"@estado": "Baixamar", "@hora": "03:40", "@altura": "1,1"},
        ],
    }


@pytest.mark.parametrize("error", [requests.Timeout, requests.ConnectionError])
@responses.activate
def test_tide_network_errors_return_none(tide_url, error):
    responses.get(tide_url, body=error("Simulated network failure"))

    assert MeteoGalicia().get_forecast_tide("3") is None


@pytest.mark.parametrize(
    "body", ["", "<rss><channel>", "<html>Unavailable"],
    ids=["empty", "truncated-xml", "invalid-html"],
)
@responses.activate
def test_invalid_xml_returns_none(tide_url, body):
    responses.get(tide_url, body=body, content_type="application/xml")

    assert MeteoGalicia().get_forecast_tide("3") is None


@pytest.mark.parametrize(
    "indices", [[], [1], [0, 1], [1, 2]],
    ids=["empty", "today-only", "missing-tomorrow", "missing-yesterday"],
)
@responses.activate
def test_incomplete_tide_days_return_none(tide_url, tide_items, indices):
    responses.get(tide_url, body=_rss([tide_items[i] for i in indices]))

    assert MeteoGalicia().get_forecast_tide("3") is None


@pytest.mark.parametrize("missing", ["tides", "port"])
@responses.activate
def test_missing_tide_fields_return_none(tide_url, tide_items, missing):
    tide_items[0] = _item(
        datetime(2025, 12, 31), "01",
        include_tides=missing != "tides", include_port=missing != "port",
    )
    responses.get(tide_url, body=_rss(tide_items))

    assert MeteoGalicia().get_forecast_tide("3") is None


@responses.activate
def test_tide_days_are_selected_by_date(tide_url, tide_items):
    responses.get(tide_url, body=_rss([tide_items[2], tide_items[0], tide_items[1]]))

    data = MeteoGalicia().get_forecast_tide("3")

    assert data is not None
    assert data["yesterdayLastTide"]["@hora"] == "01:40"
    assert data["todayTides"][0]["@hora"] == "02:10"
    assert data["tomorrowFirstTide"]["@hora"] == "03:10"


@pytest.mark.parametrize(
    "today,start,end",
    [
        (datetime(2026, 1, 1), "31/12/2025", "02/01/2026"),
        (datetime(2026, 3, 1), "28/02/2026", "02/03/2026"),
        (datetime(2024, 3, 1), "29/02/2024", "02/03/2024"),
    ],
    ids=["year-boundary", "month-boundary", "leap-year"],
)
@responses.activate
def test_tide_request_date_window(monkeypatch, today, start, end):
    class FrozenDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return today.replace(tzinfo=tz)

    monkeypatch.setattr(interface, "datetime", FrozenDateTime)
    url = URL_FORECAST_TIDE.format("3", start, end)
    items = [
        _item(today + timedelta(days=offset), f"{offset + 2:02}")
        for offset in [-1, 0, 1]
    ]
    responses.get(url, body=_rss(items))

    data = MeteoGalicia().get_forecast_tide("3")

    assert data is not None
    assert data["todayTides"][0]["@hora"] == "02:10"
    assert responses.calls[0].request.url == url


@responses.activate
def test_tide_window_uses_galicia_date_near_utc_midnight(monkeypatch):
    """The API calendar day must not depend on the host's timezone."""
    class FrozenDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            utc_now = cls(2026, 1, 1, 23, 30, tzinfo=ZoneInfo("UTC"))
            return utc_now.astimezone(tz)

    monkeypatch.setattr(interface, "datetime", FrozenDateTime)
    url = URL_FORECAST_TIDE.format("3", "01/01/2026", "03/01/2026")
    items = [_item(datetime(2026, 1, day), "02") for day in (1, 2, 3)]
    responses.get(url, body=_rss(items))
    data = MeteoGalicia().get_forecast_tide("3")
    assert data["todayDate"] == "2026-01-02"
    assert data["date"] == "2026-01-02T00:00:00Z"


@responses.activate
def test_tide_day_falls_back_to_utc_timestamp(tide_url, tide_items):
    """UTC midnight metadata can represent the previous UTC calendar day."""
    import re
    tide_items[1] = re.sub(
        r"<Mareas:dataPredicion.*?</Mareas:dataPredicion>", "", tide_items[1]
    ).replace("2026-01-01T00:00:00Z", "2025-12-31T23:00:00Z")
    responses.get(tide_url, body=_rss(tide_items))
    data = MeteoGalicia().get_forecast_tide("3")
    assert data["todayDate"] == "2026-01-01"


@responses.activate
def test_single_tide_is_normalized_to_list(tide_url, tide_items):
    """A singleton XML element must not become a mapping of tide fields."""
    import re
    tide_items[1] = re.sub(
        r'<Mareas:mareas estado="Baixamar".*?/>', "", tide_items[1]
    )
    responses.get(tide_url, body=_rss(tide_items))
    data = MeteoGalicia().get_forecast_tide("3")
    assert len(data["todayTides"]) == 1
    assert data["todayTides"][0]["@hora"] == "02:10"


@responses.activate
def test_invalid_prediction_date_returns_none(tide_url, tide_items):
    tide_items[1] = tide_items[1].replace("01/01/2026", "invalid")
    responses.get(tide_url, body=_rss(tide_items))
    assert MeteoGalicia().get_forecast_tide("3") is None
