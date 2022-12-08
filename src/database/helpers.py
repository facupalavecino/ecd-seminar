from typing import Any, List

from airflow.hooks.postgres_hook import PostgresHook
from jinja2 import Template  # type: ignore

from src.cfg import POSTGRES_CONN_ID, SQL_QUERIES_DIR


def get_city_coordinates_from_db(city_name: str, country: str) -> Any:
    """Returns the geo coordinates of a city from the database

    Parameters
    ----------
    city_name : str
        Name of the city
    country : str
        Name of the country

    Returns
    -------
    A list of records
    """
    pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)

    with open(SQL_QUERIES_DIR / "get_city_coordinates.sql", "r", encoding="utf-8") as f:
        template = Template(f.read())

    query = template.render({"city_name": city_name, "country": country})

    return pg_hook.get_records(sql=query)


def save_city_coordinates_in_db(
    city_name: str,
    country: str,
    lat: float,
    lon: float,
) -> int:
    """Saves the geo coordinates of a city in the database

    Parameters
    ----------
    city_name : str
        Name of the city
    country : str
        Name of the country
    lat: float
        City's latitude to save
    lon : float
        City's longitude to save

    Returns
    -------
    int : The ID of the new or existing record
    """
    pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)

    with open(
        SQL_QUERIES_DIR / "insert_city_coordinates.sql", "r", encoding="utf-8"
    ) as f:
        template = Template(f.read())

    query = template.render(
        {"city_name": city_name, "country": country, "lat": lat, "lon": lon}
    )

    with pg_hook.get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            idx = cursor.fetchone()[0]

    return idx


def save_weather_measurement_in_db(
    city_id: int,
    measurements: List[Any],
):
    """Saves the hourly weather measurements of a city in the database

    Parameters
    ----------
    city_id : int
        ID of the city
    measurements : List[Any]
        Tuple containing several weather measurements for each hour for the city
    """
    pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)

    with open(
        SQL_QUERIES_DIR / "insert_weather_measurement.sql", "r", encoding="utf-8"
    ) as f:
        template = Template(f.read())

    query = template.render(
        {
            "city_id": city_id,
            "measurements": measurements,
        }
    )

    with pg_hook.get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
