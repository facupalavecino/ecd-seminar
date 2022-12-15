import os
from datetime import datetime, timedelta
from pathlib import Path
from sys import path
from typing import List, Tuple

from airflow.models.dag import DAG
from airflow.models.taskinstance import TaskInstance
from airflow.operators.dummy import DummyOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python import (
    BranchPythonOperator,
    PythonOperator,
    get_current_context,
)
from airflow.utils.task_group import TaskGroup
from airflow.utils.trigger_rule import TriggerRule

path.extend(["/ecd-intensive-seminar", str(Path(__file__).parents[2])])

from src.api.helpers import get_city_coordinates, get_city_weather
from src.cfg import POSTGRES_CONN_ID
from src.database.helpers import get_city_coordinates_from_db

LOCATIONS: List[Tuple[str, str]] = [
    ("Buenos Aires", "AR"),
    ("London", "GB"),
    ("Paris", "FR"),
    ("Doha", "QA"),
]


def check_city_coordinates(city_name: str, country: str) -> str:
    """Checks if the geo coordinates of a city are stored in the database.

    If yes, they are pushed through an XCom.

    Parameters
    ----------
    city_name : str
        Name of the city
    country : str
        Name of the country
    """
    context = get_current_context()

    logical_date: datetime = context["logical_date"]

    ti: TaskInstance = context["ti"]

    records = get_city_coordinates_from_db(city_name=city_name, country=country)

    if len(records) > 0:
        city_id = int(records[0][0])
        lat = float(records[0][1])
        lon = float(records[0][2])

        logical_date_formatted = logical_date.strftime("%Y-%m-%d")

        ti.xcom_push(
            key=f"{city_name}_{country}_coordinates_{logical_date_formatted}",
            value=[city_id, lat, lon],
        )

        return f"{city_name.replace(' ', '-')}_{country}.bypass"

    return f"{city_name.replace(' ', '-')}_{country}.get_city_coordinates"


def get_city_coordinates_from_api(city_name: str, country: str):
    """Requests the geo coordinates of a city from the API.

    The result is pushed through an XCom.

    Parameters
    ----------
    city_name : str
        Name of the city
    country : str
        Name of the country
    """
    context = get_current_context()

    logical_date: datetime = context["logical_date"]

    ti: TaskInstance = context["ti"]

    city_id, lat, lon = get_city_coordinates(city_name=city_name, country=country)

    ti.xcom_push(
        key=f"{city_name}_{country}_coordinates_{logical_date.strftime('%Y-%m-%d')}",
        value=[city_id, lat, lon],
    )


def get_city_weather_from_api(city_name: str, country: str):
    """Requests the historical weather of a city from the API.

    Parameters
    ----------
    city_name : str
        Name of the city
    country : str
        Name of the country
    """
    context = get_current_context()

    logical_date: datetime = context["logical_date"]

    ti: TaskInstance = context["ti"]

    coords = ti.xcom_pull(
        task_ids=[
            f"{city_name.replace(' ', '-')}_{country}.get_city_coordinates",
            f"{city_name.replace(' ', '-')}_{country}.check_coordinates",
        ],
        key=f"{city_name}_{country}_coordinates_{logical_date.strftime('%Y-%m-%d')}",
    )

    city_id, lat, lon = coords[0] or coords[1]

    get_city_weather(
        city_id=city_id, lat=lat, lon=lon, logical_date=logical_date - timedelta(days=7)
    )


with DAG(
    dag_id="current_weather",
    description="Fetches the hourly weather for a series of cities around the world",
    schedule_interval="@daily",
    start_date=datetime(2022, 9, 1, 0, 0, 0),
    catchup=True,
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=5),
) as dag:

    create_pet_table = PostgresOperator(
        postgres_conn_id=POSTGRES_CONN_ID,
        task_id="create_cities_table",
        sql="sql/create_cities_table.sql",
        params={"user": os.environ["POSTGRES_USER"]},
    )

    for city, country_name in LOCATIONS:

        with TaskGroup(
            group_id=f"{city.replace(' ', '-')}_{country_name}",
        ) as city_group:

            check_coordinates = BranchPythonOperator(
                task_id="check_coordinates",
                python_callable=check_city_coordinates,
                op_kwargs={"city_name": city, "country": country_name},
                depends_on_past=False,
                provide_context=True,
            )

            get_geo = PythonOperator(
                task_id="get_city_coordinates",
                python_callable=get_city_coordinates_from_api,
                op_kwargs={"city_name": city, "country": country_name},
                depends_on_past=False,
            )

            bypass = DummyOperator(task_id="bypass")

            get_weather = PythonOperator(
                task_id="get_current_weather",
                python_callable=get_city_weather_from_api,
                op_kwargs={"city_name": city, "country": country_name},
                depends_on_past=False,
                trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
                provide_context=True,
            )

            end = DummyOperator(
                task_id="end", trigger_rule=TriggerRule.ONE_SUCCESS
            )  # pylint: disable=pointless-statement

            (  # pylint: disable=pointless-statement
                check_coordinates >> [get_geo, bypass] >> get_weather >> end
            )  # pylint: disable=pointless-statement

            create_pet_table >> city_group  # pylint: disable=pointless-statement
