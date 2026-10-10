"""Errors available to clients that opt in to strict error handling."""

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from math import isfinite


class MeteoGaliciaError(Exception):
    """Base error, with a stable diagnostic category and retry policy."""

    kind = "api"
    retryable = False
    retry_after = None


class MeteoGaliciaConnectionError(MeteoGaliciaError):
    kind = "connection"
    retryable = True


class MeteoGaliciaTimeoutError(MeteoGaliciaConnectionError):
    kind = "timeout"


class MeteoGaliciaInvalidResponseError(MeteoGaliciaError):
    kind = "invalid_response"


class MeteoGaliciaNoDataError(MeteoGaliciaError):
    kind = "no_data"
    retryable = True


class MeteoGaliciaHTTPError(MeteoGaliciaError):
    kind = "http"

    def __init__(self, status_code, retry_after=None):
        super().__init__(f"MeteoGalicia returned HTTP {status_code}")
        self.status_code = status_code
        self.retryable = status_code == 429 or status_code >= 500
        self.retry_after = retry_after if self.retryable else None


def retry_after_seconds(value, now=None):
    """Parse Retry-After seconds or an HTTP date; ignore invalid values."""
    if not isinstance(value, str):
        return None
    try:
        seconds = float(value)
    except ValueError:
        try:
            deadline = parsedate_to_datetime(value)
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=timezone.utc)
            seconds = (deadline - (now or datetime.now(timezone.utc))).total_seconds()
            return max(0.0, seconds)
        except (TypeError, ValueError, OverflowError):
            return None
    return seconds if isfinite(seconds) and seconds >= 0 else None
