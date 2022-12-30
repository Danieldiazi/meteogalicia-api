"""Client for the Meteogalicia REST API."""
import logging
from datetime import datetime, timedelta

import requests
URL_FORECAST = "https://servizos.meteogalicia.gal/mgrss/predicion/jsonPredConcellos.action?idConc={}"
URL_OBSERVATION = "https://servizos.meteogalicia.gal/mgrss/observacion/observacionConcellos.action?idConcello={}"


_LOGGER = logging.getLogger(__name__)

class MeteoGalicia:
    """Class to interact with the MeteoGalicia web service."""
    def __init__( self,  log_level=logging.WARNING):
        logging.getLogger().setLevel(log_level)
        self._session = requests.Session()
    
    def _do_get(self, url, id):
        result = None
        r = self._session.get(url.format(id),timeout=15)
        if r.status_code == 200:
                _LOGGER.debug("data received for %s", id)
                
                result = r.json()
        else:
                _LOGGER.error("error code %s for %s - returned: %s",  r.status_code,
                    id,
                    r.text,
                    
                )
        return result

    def get_forecast_data(self,id):
        r = self._do_get(URL_FORECAST,id)
        if (r==None ):
            _LOGGER.error("No data for %s", id)
        elif ((r['predConcello'])==None):
                _LOGGER.debug("No forecast data for %s", id)
        return r
    
    def get_observation_data(self,id):
        r = self._do_get(URL_OBSERVATION,id)
        if (r==None):
            _LOGGER.error("No data for %s", id)
        elif (len(r['listaObservacionConcellos'])==0):
             _LOGGER.debug("No observation data for %s", id)
        return r
    

