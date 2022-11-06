import json
import requests

from datetime import datetime

from src.cfg import (
    OPEN_WEATHER_BASE_URL,
    OPEN_WEATHER_API_KEY,
)
from src.database.helpers import save_city_coordinates_in_db


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
        url=OPEN_WEATHER_BASE_URL + "/geo/1.0/direct",
        params={
            "q": f"{city_name}, {country}",
            "appid": OPEN_WEATHER_API_KEY
        }
    )

    r.raise_for_status()

    data = json.loads(r.content)[0]

    lat = data["lat"]
    lon = data["lon"]

    save_city_coordinates_in_db(
        city_name=city_name,
        country=country,
        lat=lat,
        lon=lon,
    )

    return lat, lon


def get_city_weather(city_id: int, lat: float, lon: float, logical_date: datetime):
    """Makes an HTTP request to get a city's current weather 
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

    r = requests.get(
        url=OPEN_WEATHER_BASE_URL + "/data/2.5/weather",
        params={
            "lat": lat,
            "lon": lon,
            "appid": OPEN_WEATHER_API_KEY
        }
    )

    r.raise_for_status()

    data = r.json()

    temperature = data["main"]["temp"] - 273
    feels_like = data["main"]["feels_like"] - 273
    pressure = data["main"]["pressure"]
    humidity = data["main"]["humidity"]

    print(f"""
        - Date: {logical_date}
        - City ID: {city_id}
        - Temp: {temperature}
        - Feels Like: {feels_like}
        - pressure: {pressure}
        - humidity: {humidity}
    """)

    # pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)

    # with open(SQL_QUERIES_DIR / "insert_city_coordinates.sql", "r") as f:
    #     template = Template(f.read())

    # query = template.render(
    #     {
    #         "city_name": city_name,
    #         "country": country,
    #         "lat": lat,
    #         "lon": lon
    #     }
    # )

    # with pg_hook.get_conn() as conn:
    #     with conn.cursor() as cursor:
    #         cursor.execute(query)

    # return lat, lon
