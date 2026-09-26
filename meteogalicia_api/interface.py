"""Client for the Meteogalicia REST API."""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from xml.parsers.expat import ExpatError
import requests
import xmltodict

from .const import (
    URL_FORECAST,
    URL_FORECAST_HOURLY,
    URL_FORECAST_MEDIUM_TERM,
    URL_FORECAST_TIDE,
    URL_WARNINGS,
    URL_MAX_WARNING_LEVELS,
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
    
    def _do_get(self, url, *args) -> Optional[Dict[str, Any]]:
        result = None
        identifier = args[0] if args else "unknown"
        try:
            r = self._session.get(url.format(*args), timeout=self._timeout)
            r.raise_for_status()
            self.logger.debug(f"Data received for {identifier}")
            result = r.json()
        except requests.exceptions.RequestException as exc:
            self.logger.error(f"Request error for code: {identifier} - {exc}")
        except ValueError as exc:
            self.logger.error(f"Invalid JSON for code: {identifier} - {exc}")
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
        elif r.get("predConcello") is None:
                self.logger.debug(f"No forecast data for {id}")
                return None
        return r
    
    def get_hourly_forecast_data(self, id) -> Optional[Dict[str, Any]]:
        """Return the original hourly forecast JSON, or None when unavailable."""
        r = self._do_get(URL_FORECAST_HOURLY,id)
        pred = r.get('predHoraria') if isinstance(r, dict) else None
        days = pred.get('listaPredDiaHoraria') if isinstance(pred, dict) else None
        if not isinstance(days, list) or not days:
            # An unknown code also returns 200 with an empty list.
            self.logger.debug(f"No hourly forecast data for code: {id}")
            return None
        return r

    def get_medium_term_forecast_data(self, id) -> Optional[Dict[str, Any]]:
        """Return the original medium term forecast JSON, or None when unavailable."""
        r = self._do_get(URL_FORECAST_MEDIUM_TERM,id)
        pred = r.get('predMPrazo') if isinstance(r, dict) else None
        days = pred.get('listaPredDiaMPrazo') if isinstance(pred, dict) else None
        if not isinstance(days, list) or not days:
            # An unknown code also returns 200 with an empty list.
            self.logger.debug(f"No medium term forecast data for code: {id}")
            return None
        return r

    def get_warnings_data(self, id, day=-1) -> Optional[Dict[str, Any]]:
        """Return detailed municipal weather warnings, including an empty valid list."""
        return self._get_warning_days(URL_WARNINGS, id, day, "listaAvisosConcellos")

    def get_max_warning_levels_data(self, id, day=-1) -> Optional[Dict[str, Any]]:
        """Return MeteoGalicia's maximum warning level for the requested day(s)."""
        return self._get_warning_days(URL_MAX_WARNING_LEVELS, id, day, "listaNiveisMaximos")

    def _get_warning_days(self, url, id, day, list_key) -> Optional[Dict[str, Any]]:
        """Validate daily warning lists while preserving the original JSON."""
        r = self._do_get(url, id, day)
        days = r.get("listaDiaConcellos") if isinstance(r, dict) else None
        if not isinstance(days, list) or any(
            not isinstance(item, dict) or not isinstance(item.get(list_key), list)
            for item in days
        ):
            self.logger.debug(f"No valid {list_key} data for code: {id}")
            return None
        return r

    def get_observation_data(self, id) -> Optional[Dict[str, Any]]:
        r = self._do_get(URL_OBSERVATION,id)
        if (r==None):
            self.logger.error(f"No data for code: {id}")
            return None
        elif len(r.get("listaObservacionConcellos", [])) == 0:
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
