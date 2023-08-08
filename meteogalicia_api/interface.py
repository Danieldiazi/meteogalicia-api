"""Client for the Meteogalicia REST API."""
import logging
from datetime import datetime, timedelta
import requests

URL_FORECAST = "https://servizos.meteogalicia.gal/mgrss/predicion/jsonPredConcellos.action?idConc={}"
URL_OBSERVATION = "https://servizos.meteogalicia.gal/mgrss/observacion/observacionConcellos.action?idConcello={}"
URL_OBSERVATION_DAILYDATA_BY_STATION="https://servizos.meteogalicia.gal/mgrss/observacion/datosDiariosEstacionsMeteo.action?idEst={}"
URL_OBSERVATION_LAST10MINDATA_BY_STATION="https://servizos.meteogalicia.gal/mgrss/observacion/ultimos10minEstacionsMeteo.action?idEst={}"


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
    
    def get_observation_dailydata_by_station(self,id):
        r = self._do_get(URL_OBSERVATION_DAILYDATA_BY_STATION,id)
        if (r==None) or (not('listDatosDiarios1' in r)) or (len(r['listDatosDiarios'])==0):
             self.logger.debug(f"No observation info (daily data) of station code: {id}")      
        return r
    
    def get_observation_last10mindata_by_station(self,id):
        r = self._do_get(URL_OBSERVATION_LAST10MINDATA_BY_STATION,id)
        if (r==None) or (not('listUltimos10min1' in r)) or (len(r['listUltimos10min'])==0):
             self.logger.debug(f"No observation info (last 10 min data) of station code: {id}")
        return r