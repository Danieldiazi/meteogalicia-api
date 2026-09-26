
![PyPI](https://img.shields.io/pypi/v/MeteoGalicia-API)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/MeteoGalicia-API)

Description
-----------

MeteoGalicia-API implements an interface to the MeteoGalicia Rest web services.

Documentation about MeteoGalicia web service is available at https://www.meteogalicia.gal/web/RSS/rssIndex.action?request_locale=es.

This package has been developed to be used with  [homeassistant-meteogalicia](https://github.com/Danieldiazi/homeassistant-meteogalicia)  integration for [Home-Assistant](https://home-assistant.io/)

Disclaimer
----------

This software is provided without warranty, and should therefore not be used where it may endanger life, financial stakes, or cause discomfort and inconvenience to others. Is also licensed under the GNU Public Licence version 3

Usage
-----

Example:
```python
from meteogalicia_api.interface import MeteoGalicia
meteogalicia = MeteoGalicia()
meteogalicia.get_forecast_data("32054")
meteogalicia.get_observation_data("15023")
```

Custom session and timeout:
```python
import requests
from meteogalicia_api.interface import MeteoGalicia

session = requests.Session()
meteogalicia = MeteoGalicia(session=session, timeout=10)
meteogalicia.get_forecast_data("32054")
```

Town hall or city data methods:
```python
meteogalicia.get_forecast_data("32054")
meteogalicia.get_hourly_forecast_data("32054")
meteogalicia.get_medium_term_forecast_data("32054")
meteogalicia.get_warnings_data("32054")
meteogalicia.get_max_warning_levels_data("32054")
meteogalicia.get_observation_data("15023")
```
Parameter id's are available at https://www.meteogalicia.gal/datosred/infoweb/meteo/docs/rss/JSON_Pred_Concello_es.pdf 

Hourly and medium term forecasts:

Both methods return the original JSON dictionary, including the forecast wrapper.
They return `None` if the request fails, the forecast container is missing or is
not an object, or its prediction list is missing, empty or is not a list. Individual
records are returned unchanged; the client does not validate every field.

| Method | Prediction list in the returned dictionary | Main fields |
| --- | --- | --- |
| `get_hourly_forecast_data(id)` | `data["predHoraria"]["listaPredDiaHoraria"]` | Each day contains `dia` and `listaPredHora`; each hour contains `dataPredicion`, `tMedia`, `icoCeo` and `icoVento`. |
| `get_medium_term_forecast_data(id)` | `data["predMPrazo"]["listaPredDiaMPrazo"]` | Each day contains `dataPredicion`, `dia`, `tMin`, `tMax`, sky condition alternatives and their probabilities. |

- Hourly `dataPredicion` values use local time in Galicia (`Europe/Madrid`) and
  contain no UTC offset. The client does not convert them to UTC. Consumers must
  account for the local time zone and daylight saving changes.
- MeteoGalicia uses `-9999` for unavailable weather values. The client preserves
  this sentinel; consumers should treat it as missing data, not as a temperature,
  probability or valid weather code.
- Medium term `icoCeo1`, `icoCeo2` and `icoCeo3` are possible sky conditions with
  corresponding `probIcoCeo1`, `probIcoCeo2` and `probIcoCeo3` probabilities. They
  are not morning, afternoon and night forecasts. Use the probabilities when
  choosing a representative condition.
- The medium term forecast starts after the short term forecast. The number of
  days and hours varies with availability; combine daily forecasts using their
  dates rather than assuming fixed list lengths.

```python
data = meteogalicia.get_hourly_forecast_data("15030")
if data is not None:
    for day in data["predHoraria"]["listaPredDiaHoraria"]:
        for hour in day["listaPredHora"]:
            temperature = hour.get("tMedia")
            if temperature is not None and temperature != -9999:
                print(hour["dataPredicion"], temperature)
```

Official response schemas and weather codes:
[hourly forecast](https://www.meteogalicia.gal/datosred/infoweb/meteo/docs/rss/JSON_Pred_Horaria_Concello_es.pdf)
and [medium term forecast](https://www.meteogalicia.gal/datosred/infoweb/meteo/docs/rss/JSON_Pred_MPrazo_es.pdf).

Warning methods:

```python
# Detailed warnings: level, alert type and validity period.
warnings = meteogalicia.get_warnings_data("15030", day=-1)

# MeteoGalicia's own maximum warning level summary.
levels = meteogalicia.get_max_warning_levels_data("15030", day=-1)
```

The optional `day` argument accepts `0` (today), `1` (tomorrow), `2`
(the day after tomorrow) and `-1` (all available days). Both methods return
the original MeteoGalicia JSON dictionary when the expected list is present.
An empty list is a valid response: for detailed warnings it means there are no
warnings for that query. Malformed responses and request failures return `None`.

- `get_warnings_data()` uses `jsonAvisosConcellos.action` and exposes individual
  warnings, including `idNivel`, `dataAviso`, `dataIni`, `dataFin`,
  `idTipoAlerta`, `tipoalerta_gl` and `tipoalerta_es`.
- `get_max_warning_levels_data()` uses `jsonConcellosNivelMax.action` and exposes
  MeteoGalicia's `nivelMax` summary (0 normal, 1 yellow, 2 orange, 3 red).

Official documentation:
[complete municipal warnings](https://meteo-estaticos.xunta.gal/datosred/infoweb/meteo/docs/rss/JSON_Pred_AvisoConcello_gl.pdf)
and [maximum municipal warning level](https://meteo-estaticos.xunta.gal/datosred/infoweb/meteo/docs/rss/JSON_Pred_AvisoConcelloNivelMax_gl.pdf).

Station methods:
```python
meteogalicia.get_observation_dailydata_by_station("10144")
meteogalicia.get_observation_last10mindata_by_station("10144")
```
Parameter station id's are available at https://servizos.meteogalicia.gal/mgrss/observacion/listaEstacionsMeteo.action

Tides methods:

```python
meteogalicia.get_forecast_tide("3")
```
id availables at: https://www.meteogalicia.gal/datosred/infoweb/meteo/docs/rss/RSS_Mareas_gl.pdf

Errors:
- Methods return `None` when no data is available or the request fails.
