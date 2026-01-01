"""Client for the Meteogalicia REST API."""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from xml.parsers.expat import ExpatError
import requests
import xmltodict

from .const import (
    URL_FORECAST,
    URL_FORECAST_TIDE,
    URL_OBSERVATION,
    URL_OBSERVATION_DAILYDATA_BY_STATION,
    URL_OBSERVATION_LAST10MINDATA_BY_STATION,
)

class MeteoGalicia:
    """Class to interact with the MeteoGalicia web service."""
    def __init__(self, log_level=logging.WARNING, session=None, timeout=15):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        self._session = session if session is not None else requests.Session()
        self._timeout = timeout
    
    def _do_get(self, url, id) -> Optional[Dict[str, Any]]:
        result = None
        try:
            r = self._session.get(url.format(id), timeout=self._timeout)
            r.raise_for_status()
            self.logger.debug(f"Data received for {id}")
            result = r.json()
        except requests.exceptions.RequestException as exc:
            self.logger.error(f"Request error for code: {id} - {exc}")
        except ValueError as exc:
            self.logger.error(f"Invalid JSON for code: {id} - {exc}")
        return result

    def _do_getGeoRSS(self, url, id, date1, date2) -> Optional[Dict[str, Any]]:
        result = None
        try:
            r = self._session.get(url.format(id, date1, date2), timeout=self._timeout)
            r.raise_for_status()
            self.logger.debug(f"Data received for {id}")
            xml_data = r.text
            data_dict = xmltodict.parse(xml_data)
            result = data_dict
        except requests.exceptions.RequestException as exc:
            self.logger.error(f"Request error for code: {id} - {exc}")
        except ExpatError as exc:
            self.logger.error(f"Invalid XML for code: {id} - {exc}")
        return result

    def get_forecast_data(self, id) -> Optional[Dict[str, Any]]:
        r = self._do_get(URL_FORECAST,id)
        if (r==None ):
            self.logger.error(f"No data for code: {id}")
            return None
        elif ((r['predConcello'])==None):
                self.logger.debug(f"No forecast data for {id}")
                return None
        return r
    
    def get_observation_data(self, id) -> Optional[Dict[str, Any]]:
        r = self._do_get(URL_OBSERVATION,id)
        if (r==None):
            self.logger.error(f"No data for code: {id}")
            return None
        elif (len(r['listaObservacionConcellos'])==0):
             self.logger.debug(f"No observation data for {id}")
             return None
        return r
    
    def get_observation_dailydata_by_station(self, id) -> Optional[Dict[str, Any]]:
        r = self._do_get(URL_OBSERVATION_DAILYDATA_BY_STATION,id)
        if (r==None) or (not('listDatosDiarios' in r)) or (len(r['listDatosDiarios'])==0):
             self.logger.debug(f"No observation info (daily data) of station code: {id}")      
             return None
        return r
    
    def get_observation_last10mindata_by_station(self, id) -> Optional[Dict[str, Any]]:
        r = self._do_get(URL_OBSERVATION_LAST10MINDATA_BY_STATION,id)
        if (r==None) or (not('listUltimos10min' in r)) or (len(r['listUltimos10min'])==0):
             self.logger.debug(f"No observation info (last 10 min data) of station code: {id}")
             return None
        return r
    
    def get_forecast_tide(self, id) -> Optional[Dict[str, Any]]:
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        tomorrow =  today + timedelta(days=1)
        strYesterday = yesterday.strftime("%d/%m/%Y")
        strTomorrow = tomorrow.strftime("%d/%m/%Y")
        data = None

        r = self._do_getGeoRSS(URL_FORECAST_TIDE,id,strYesterday,strTomorrow)
        
        if (r==None):
            self.logger.error(f"Unavailable forecast tide data for code: {id}")
        else:
            rss = r.get("rss") if isinstance(r, dict) else None
            channel = rss.get("channel") if isinstance(rss, dict) else None
            items = channel.get("item") if isinstance(channel, dict) else None
            if not isinstance(items, list):
                self.logger.error(f"Unexpected tide payload for code: {id}")
                return None
            try:
                yesterdayTidesArrayLen = len(items[0]['Mareas:mareas'])
                data = {}
                data["pointGeoRSS"] = items[0]['georss:point']
                data["date"] = items[0]['dc:date']
                data["portId"] = items[0]['Mareas:idPorto']["#text"]
                data["portName"] = items[0]['Mareas:nomePorto']["#text"]
                data["yesterdayLastTide"] = items[0]['Mareas:mareas'][yesterdayTidesArrayLen-1]
                data["todayTides"] = items[1]['Mareas:mareas']
                data["tomorrowFirstTide"] = items[2]['Mareas:mareas'][0]
            except (KeyError, IndexError, TypeError) as exc:
                self.logger.error(f"Unexpected tide payload for code: {id} - {exc}")
                return None

             

             

        return data
