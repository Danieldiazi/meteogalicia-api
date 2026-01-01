
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
meteogalicia.get_observation_data("15023")
```
Parameter id's are available at https://www.meteogalicia.gal/datosred/infoweb/meteo/docs/rss/JSON_Pred_Concello_es.pdf 

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
