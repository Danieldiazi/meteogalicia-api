from datetime import datetime, timedelta

import responses

from meteogalicia_api.interface import (
    MeteoGalicia,
    URL_FORECAST,
    URL_OBSERVATION,
    URL_FORECAST_TIDE,
)


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


@responses.activate
def test_get_forecast_tide_ok():
    api = MeteoGalicia()
    today = datetime.now()
    str_yesterday = (today - timedelta(days=1)).strftime("%d/%m/%Y")
    str_tomorrow = (today + timedelta(days=1)).strftime("%d/%m/%Y")
    xml_body = """<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:georss="http://www.georss.org/georss" xmlns:Mareas="Mareas" version="2.0">
  <channel>
    <title>Táboa de mareas</title>
    <link>https://www.meteogalicia.gal/web/predicion/mareas-e-luas?request_locale=gl</link>
    <description>Mareas amosadas en horario local</description>
    <item>
      <title>Mareas en Vigo para  mércores 31 de decembro</title>
      <link>https://www.meteogalicia.gal/web/predicion/mareas-e-luas?request_locale=gl&amp;idPorto=3&amp;data=31/12/2025</link>
      <description>&lt;div  id="divestActual" class="datos"&gt;&lt;table class="tableloc"  width=250 border=1 bordercolor="#cfcfcf"&gt;&lt;thead&gt;&lt;th&gt;Estado&lt;/th&gt;&lt;th&gt;Hora&lt;/th&gt;&lt;th&gt;Altura&lt;/th&gt;&lt;/thead&gt;&lt;tr&gt;&lt;td&gt;Preamar&lt;/td&gt;&lt;td&gt;00:33&lt;/td&gt;&lt;td&gt;3.2&lt;/td&gt;&lt;/tr&gt;&lt;tr&gt;&lt;td&gt;Baixamar&lt;/td&gt;&lt;td&gt;06:46&lt;/td&gt;&lt;td&gt;1.1&lt;/td&gt;&lt;/tr&gt;&lt;tr&gt;&lt;td&gt;Preamar&lt;/td&gt;&lt;td&gt;13:03&lt;/td&gt;&lt;td&gt;3.3&lt;/td&gt;&lt;/tr&gt;&lt;tr&gt;&lt;td&gt;Baixamar&lt;/td&gt;&lt;td&gt;19:14&lt;/td&gt;&lt;td&gt;1.0&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;&lt;/div&gt;&lt;br/&gt;</description>
      <pubDate>Tue, 30 Dec 2025 23:00:00 GMT</pubDate>
      <guid>https://www.meteogalicia.gal/web/predicion/mareas-e-luas?request_locale=gl&amp;idPorto=3&amp;data=31/12/2025</guid>
      <dc:date>2025-12-30T23:00:00Z</dc:date>
      <georss:point>42.233333587646484 -8.716667175292969</georss:point>
      <Mareas:nomePorto descricion="Porto">Vigo</Mareas:nomePorto>
      <Mareas:idPorto descricion="IdPorto">3</Mareas:idPorto>
      <Mareas:idPortoRef descricion="IdPortoRef">3</Mareas:idPortoRef>
      <Mareas:dataPredicion formato="dd/MM/yyyy">31/12/2025</Mareas:dataPredicion>
      <Mareas:mareas id="0" estado="Preamar" hora="00:33" altura="3,2" idTipoMarea="1" />
      <Mareas:mareas id="1" estado="Baixamar" hora="06:46" altura="1,1" idTipoMarea="0" />
      <Mareas:mareas id="2" estado="Preamar" hora="13:03" altura="3,3" idTipoMarea="1" />
      <Mareas:mareas id="3" estado="Baixamar" hora="19:14" altura="1,0" idTipoMarea="0" />
    </item>
    <item>
      <title>Mareas en Vigo para  xoves 01 de xaneiro</title>
      <link>https://www.meteogalicia.gal/web/predicion/mareas-e-luas?request_locale=gl&amp;idPorto=3&amp;data=01/01/2026</link>
      <description>&lt;div  id="divestActual" class="datos"&gt;&lt;table class="tableloc"  width=250 border=1 bordercolor="#cfcfcf"&gt;&lt;thead&gt;&lt;th&gt;Estado&lt;/th&gt;&lt;th&gt;Hora&lt;/th&gt;&lt;th&gt;Altura&lt;/th&gt;&lt;/thead&gt;&lt;tr&gt;&lt;td&gt;Preamar&lt;/td&gt;&lt;td&gt;01:34&lt;/td&gt;&lt;td&gt;3.4&lt;/td&gt;&lt;/tr&gt;&lt;tr&gt;&lt;td&gt;Baixamar&lt;/td&gt;&lt;td&gt;07:50&lt;/td&gt;&lt;td&gt;0.9&lt;/td&gt;&lt;/tr&gt;&lt;tr&gt;&lt;td&gt;Preamar&lt;/td&gt;&lt;td&gt;14:05&lt;/td&gt;&lt;td&gt;3.4&lt;/td&gt;&lt;/tr&gt;&lt;tr&gt;&lt;td&gt;Baixamar&lt;/td&gt;&lt;td&gt;20:12&lt;/td&gt;&lt;td&gt;0.9&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;&lt;/div&gt;&lt;br/&gt;</description>
      <pubDate>Wed, 31 Dec 2025 23:00:00 GMT</pubDate>
      <guid>https://www.meteogalicia.gal/web/predicion/mareas-e-luas?request_locale=gl&amp;idPorto=3&amp;data=01/01/2026</guid>
      <dc:date>2025-12-31T23:00:00Z</dc:date>
      <georss:point>42.233333587646484 -8.716667175292969</georss:point>
      <Mareas:nomePorto descricion="Porto">Vigo</Mareas:nomePorto>
      <Mareas:idPorto descricion="IdPorto">3</Mareas:idPorto>
      <Mareas:idPortoRef descricion="IdPortoRef">3</Mareas:idPortoRef>
      <Mareas:dataPredicion formato="dd/MM/yyyy">01/01/2026</Mareas:dataPredicion>
      <Mareas:mareas id="0" estado="Preamar" hora="01:34" altura="3,4" idTipoMarea="1" />
      <Mareas:mareas id="1" estado="Baixamar" hora="07:50" altura="0,9" idTipoMarea="0" />
      <Mareas:mareas id="2" estado="Preamar" hora="14:05" altura="3,4" idTipoMarea="1" />
      <Mareas:mareas id="3" estado="Baixamar" hora="20:12" altura="0,9" idTipoMarea="0" />
    </item>
    <item>
      <title>Mareas en Vigo para  venres 02 de xaneiro</title>
      <link>https://www.meteogalicia.gal/web/predicion/mareas-e-luas?request_locale=gl&amp;idPorto=3&amp;data=02/01/2026</link>
      <description>&lt;div  id="divestActual" class="datos"&gt;&lt;table class="tableloc"  width=250 border=1 bordercolor="#cfcfcf"&gt;&lt;thead&gt;&lt;th&gt;Estado&lt;/th&gt;&lt;th&gt;Hora&lt;/th&gt;&lt;th&gt;Altura&lt;/th&gt;&lt;/thead&gt;&lt;tr&gt;&lt;td&gt;Preamar&lt;/td&gt;&lt;td&gt;02:30&lt;/td&gt;&lt;td&gt;3.6&lt;/td&gt;&lt;/tr&gt;&lt;tr&gt;&lt;td&gt;Baixamar&lt;/td&gt;&lt;td&gt;08:47&lt;/td&gt;&lt;td&gt;0.7&lt;/td&gt;&lt;/tr&gt;&lt;tr&gt;&lt;td&gt;Preamar&lt;/td&gt;&lt;td&gt;15:02&lt;/td&gt;&lt;td&gt;3.5&lt;/td&gt;&lt;/tr&gt;&lt;tr&gt;&lt;td&gt;Baixamar&lt;/td&gt;&lt;td&gt;21:04&lt;/td&gt;&lt;td&gt;0.7&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;&lt;/div&gt;&lt;br/&gt;</description>
      <pubDate>Thu, 01 Jan 2026 23:00:00 GMT</pubDate>
      <guid>https://www.meteogalicia.gal/web/predicion/mareas-e-luas?request_locale=gl&amp;idPorto=3&amp;data=02/01/2026</guid>
      <dc:date>2026-01-01T23:00:00Z</dc:date>
      <georss:point>42.233333587646484 -8.716667175292969</georss:point>
      <Mareas:nomePorto descricion="Porto">Vigo</Mareas:nomePorto>
      <Mareas:idPorto descricion="IdPorto">3</Mareas:idPorto>
      <Mareas:idPortoRef descricion="IdPortoRef">3</Mareas:idPortoRef>
      <Mareas:dataPredicion formato="dd/MM/yyyy">02/01/2026</Mareas:dataPredicion>
      <Mareas:mareas id="0" estado="Preamar" hora="02:30" altura="3,6" idTipoMarea="1" />
      <Mareas:mareas id="1" estado="Baixamar" hora="08:47" altura="0,7" idTipoMarea="0" />
      <Mareas:mareas id="2" estado="Preamar" hora="15:02" altura="3,5" idTipoMarea="1" />
      <Mareas:mareas id="3" estado="Baixamar" hora="21:04" altura="0,7" idTipoMarea="0" />
    </item>
  </channel>
</rss>
"""
    responses.add(
        responses.GET,
        URL_FORECAST_TIDE.format("1", str_yesterday, str_tomorrow),
        body=xml_body,
        status=200,
    )

    data = api.get_forecast_tide("1")
    assert data["portId"] == "3"
    assert data["portName"] == "Vigo"
    assert data["yesterdayLastTide"]["@estado"] == "Baixamar"
    assert data["todayTides"][0]["@estado"] == "Preamar"
    assert data["tomorrowFirstTide"]["@estado"] == "Preamar"


@responses.activate
def test_get_forecast_tide_http_error():
    api = MeteoGalicia()
    today = datetime.now()
    str_yesterday = (today - timedelta(days=1)).strftime("%d/%m/%Y")
    str_tomorrow = (today + timedelta(days=1)).strftime("%d/%m/%Y")
    responses.add(
        responses.GET,
        URL_FORECAST_TIDE.format("3", str_yesterday, str_tomorrow),
        body="error",
        status=500,
    )

    data = api.get_forecast_tide("3")
    assert data is None


@responses.activate
def test_get_forecast_tide_unexpected_payload():
    api = MeteoGalicia()
    today = datetime.now()
    str_yesterday = (today - timedelta(days=1)).strftime("%d/%m/%Y")
    str_tomorrow = (today + timedelta(days=1)).strftime("%d/%m/%Y")
    xml_body = """<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:georss="http://www.georss.org/georss" xmlns:Mareas="Mareas" version="2.0">
  <channel>
    <item>
      <dc:date>2025-12-30T23:00:00Z</dc:date>
      <georss:point>42.0 -8.0</georss:point>
      <Mareas:nomePorto descricion="Porto">Vigo</Mareas:nomePorto>
      <Mareas:idPorto descricion="IdPorto">3</Mareas:idPorto>
      <Mareas:mareas id="0" estado="Preamar" hora="00:33" altura="3,2" idTipoMarea="1" />
    </item>
  </channel>
</rss>
"""
    responses.add(
        responses.GET,
        URL_FORECAST_TIDE.format("3", str_yesterday, str_tomorrow),
        body=xml_body,
        status=200,
    )

    data = api.get_forecast_tide("3")
    assert data is None
