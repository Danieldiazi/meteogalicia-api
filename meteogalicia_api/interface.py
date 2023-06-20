"""Client for the Meteogalicia REST API."""
import logging
from datetime import datetime, timedelta
import requests

URL_FORECAST = "https://servizos.meteogalicia.gal/mgrss/predicion/jsonPredConcellos.action?idConc={}"
URL_OBSERVATION = "https://servizos.meteogalicia.gal/mgrss/observacion/observacionConcellos.action?idConcello={}"



class MeteoGalicia:
    """Class to interact with the MeteoGalicia web service."""
    def __init__( self,  log_level=logging.WARNING):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        self._session = requests.Session()
    
    def _do_get(self, url, id):
        result = None
        r = self._session.get(url.format(id),timeout=15)
        if r.status_code == 200:
                self.logger.debug(f"Data received for {id}")
                
                result = r.json()
        else:
                self.logger.error(f"error code {r.status_code} for code: {id} - returned: {r.text}")
        return result

    def get_forecast_data(self,id):
        r = self._do_get(URL_FORECAST,id)
        if (r==None ):
            self.logger.error(f"No data for code: {id}")
        elif ((r['predConcello'])==None):
                self.logger.debug(f"No forecast data for {id}")
        return r
    
    def get_observation_data(self,id):
        r = self._do_get(URL_OBSERVATION,id)
        if (r==None):
            self.logger.error(f"No data for code: {id}")
        elif (len(r['listaObservacionConcellos'])==0):
             self.logger.debug(f"No observation data for {id}")
        return r
    

