import os
from pathlib import Path


POSTGRES_CONN_ID = "weather_postgres"

OPEN_WEATHER_BASE_URL = os.environ["OPEN_WEATHER_BASE_URL"]
OPEN_WEATHER_API_KEY = os.environ["OPEN_WEATHER_API_KEY"]

SQL_QUERIES_DIR = Path("src/dags/sql").resolve()