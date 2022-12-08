import logging
from collections import namedtuple
from datetime import datetime, timedelta

import pytz
import requests

from src.cfg import (
    HOURLY_MEASUREMENTS,
    OPEN_METEO_GEOCODING_URL,
    OPEN_METEO_HISTORY_URL,
)
from src.database.helpers import (
    save_city_coordinates_in_db,
    save_weather_measurement_in_db,
)

logger = logging.getLogger(__name__)


def get_city_coordinates(city_name: str, country: str):
    """Makes an HTTP request to get the geo coordinates of a city
    and saves the result in the database

    Parameters
    ----------
    city_name : str
        Name of the city
    country : str
        Name of the country

    Returns
    -------
    A tuple describing (city_id, latitude, longitude)
    """
    r = requests.get(
        url=OPEN_METEO_GEOCODING_URL + "/v1/search",
        params={  # type:ignore
            "name": city_name,
            "count": 1,
        },
        timeout=60,
    )

    r.raise_for_status()

    response = r.json()

    lat = response["results"][0]["latitude"]
    lon = response["results"][0]["longitude"]

    city_id = save_city_coordinates_in_db(
        city_name=city_name,
        country=country,
        lat=lat,
        lon=lon,
    )

    return city_id, lat, lon


def get_city_weather(city_id: int, lat: float, lon: float, logical_date: datetime):
    """Makes an HTTP request to get a city's historical weather
    and saves the result in the database

    Parameters
    ----------
    city_id : int
        ID of the city in the database
    lat: float
        City's latitude
    lon : float
        City's longitude
    logical_date: datetime
        Current timestamp when weather is requested
    """
    utc = pytz.UTC

    if logical_date > datetime.today().replace(tzinfo=utc) - timedelta(days=7):
        logger.warning("Historical data is available up to 1 week ago")

        return None

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": logical_date.strftime("%Y-%m-%d"),
        "end_date": logical_date.strftime("%Y-%m-%d"),
        "hourly": ",".join(HOURLY_MEASUREMENTS),
    }

    params_str = ""

    for key, val in params.items():
        params_str = params_str + f"{key}={val}&"

    params_str = params_str[:-1]  # Discard last &

    r = requests.get(
        url=OPEN_METEO_HISTORY_URL + "/v1/era5", params=params_str, timeout=60
    )

    r.raise_for_status()

    response = r.json()

    hourly = response["hourly"]

    keys = ["time"] + HOURLY_MEASUREMENTS

    t = namedtuple("WeatherData", ["time"] + HOURLY_MEASUREMENTS)  # type: ignore

    measurements = list(map(t, *[hourly[k] for k in keys]))

    save_weather_measurement_in_db(
        city_id=city_id,
        measurements=measurements,
    )

    return None
