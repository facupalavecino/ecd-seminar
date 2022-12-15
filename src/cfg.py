import os
from pathlib import Path

POSTGRES_CONN_ID = "weather_postgres"

OPEN_METEO_BASE_URL = os.environ["OPEN_METEO_BASE_URL"]
OPEN_METEO_HISTORY_URL = os.environ["OPEN_METEO_HISTORY_URL"]
OPEN_METEO_GEOCODING_URL = os.environ["OPEN_METEO_GEOCODING_URL"]

SQL_QUERIES_DIR = Path("src/dags/sql").resolve()

HOURLY_MEASUREMENTS = [
    "temperature_2m",
    "apparent_temperature",
    "surface_pressure",
    "relativehumidity_2m",
    "rain",
    "snowfall",
    "cloudcover",
    "shortwave_radiation",
]
