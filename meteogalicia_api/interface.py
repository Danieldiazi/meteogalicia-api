"""Client for the Meteogalicia REST API."""
import logging
from datetime import datetime, timedelta
import requests
import xmltodict


URL_FORECAST = "https://servizos.meteogalicia.gal/mgrss/predicion/jsonPredConcellos.action?idConc={}"
URL_OBSERVATION = "https://servizos.meteogalicia.gal/mgrss/observacion/observacionConcellos.action?idConcello={}"
URL_OBSERVATION_DAILYDATA_BY_STATION="https://servizos.meteogalicia.gal/mgrss/observacion/datosDiariosEstacionsMeteo.action?idEst={}"
URL_OBSERVATION_LAST10MINDATA_BY_STATION="https://servizos.meteogalicia.gal/mgrss/observacion/ultimos10minEstacionsMeteo.action?idEst={}"
URL_FORECAST_TIDE = "https://servizos.meteogalicia.gal/mgrss/predicion/rssMareas.action?idPorto={}&dataIni={}&dataFin={}"

class MeteoGalicia:
    """Class to interact with the MeteoGalicia web service."""
    def __init__(self, log_level=logging.WARNING, session=None, timeout=15):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        self._session = session if session is not None else requests.Session()
        self._timeout = timeout
    
    def _do_get(self, url, id):
        result = None
        r = self._session.get(url.format(id), timeout=self._timeout)
        if r.status_code == 200:
                self.logger.debug(f"Data received for {id}")
                
                result = r.json()
        else:
                self.logger.error(f"error code {r.status_code} for code: {id} - returned: {r.text}")
        return result

    def _do_getGeoRSS(self, url, id, date1, date2):
        result = None
        r = self._session.get(url.format(id, date1, date2), timeout=self._timeout)
        if r.status_code == 200:
                self.logger.debug(f"Data received for {id}")
                xml_data = r.text
                data_dict = xmltodict.parse(xml_data)
                result = data_dict
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
        if (r==None) or (not('listDatosDiarios' in r)) or (len(r['listDatosDiarios'])==0):
             self.logger.debug(f"No observation info (daily data) of station code: {id}")      
        return r
    
    def get_observation_last10mindata_by_station(self,id):
        r = self._do_get(URL_OBSERVATION_LAST10MINDATA_BY_STATION,id)
        if (r==None) or (not('listUltimos10min' in r)) or (len(r['listUltimos10min'])==0):
             self.logger.debug(f"No observation info (last 10 min data) of station code: {id}")
        return r
    
    def get_forecast_tide(self,id):
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        tomorrow =  today + timedelta(days=1)
        strYesterday = yesterday.strftime("%d/%m/%Y")
        strTomorrow = tomorrow.strftime("%d/%m/%Y")
        data = {}

        r = self._do_getGeoRSS(URL_FORECAST_TIDE,id,strYesterday,strTomorrow)
        
        if (r==None):
            self.logger.error(f"Unavailable forecast tide data for code: {id}")
        elif (len(r['rss'])==0):
             self.logger.debug(f"No forecast tide data for {id}")
        else: 
             
             yesterdayTidesArrayLen=len(r['rss']['channel']['item'][0]['Mareas:mareas'])

             data["pointGeoRSS"] = r['rss']['channel']['item'][0]['georss:point']
             data["date"] = r['rss']['channel']['item'][0]['dc:date']
             data["portId"] = r['rss']['channel']['item'][0]['Mareas:idPorto']["#text"]
             data["portName"] = r['rss']['channel']['item'][0]['Mareas:nomePorto']["#text"]
             data["yesterdayLastTide"] = r['rss']['channel']['item'][0]['Mareas:mareas'][yesterdayTidesArrayLen-1]
             data["todayTides"] = r['rss']['channel']['item'][1]['Mareas:mareas']
             data["tomorrowFirstTide"] = r['rss']['channel']['item'][2]['Mareas:mareas'][0]

             

             

        return data

