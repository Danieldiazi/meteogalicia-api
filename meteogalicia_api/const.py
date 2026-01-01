"""Constants for the interface."""

URL_FORECAST = "https://servizos.meteogalicia.gal/mgrss/predicion/jsonPredConcellos.action?idConc={}"
URL_OBSERVATION = "https://servizos.meteogalicia.gal/mgrss/observacion/observacionConcellos.action?idConcello={}"
URL_OBSERVATION_DAILYDATA_BY_STATION = "https://servizos.meteogalicia.gal/mgrss/observacion/datosDiariosEstacionsMeteo.action?idEst={}"
URL_OBSERVATION_LAST10MINDATA_BY_STATION = "https://servizos.meteogalicia.gal/mgrss/observacion/ultimos10minEstacionsMeteo.action?idEst={}"
URL_FORECAST_TIDE = "https://servizos.meteogalicia.gal/mgrss/predicion/rssMareas.action?idPorto={}&dataIni={}&dataFin={}"
