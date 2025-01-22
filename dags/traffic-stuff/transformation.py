import os
from datetime import datetime
from pathlib import Path

from airflow.decorators import dag

from cosmos import DbtTaskGroup, ProfileConfig, ProjectConfig
from cosmos.profiles import PostgresUserPasswordProfileMapping
from airflow.datasets import Dataset

DBT_ROOT_PATH = Path(os.getenv("AIRFLOW_HOME")) / "dags" / "dbt"


profile_config = ProfileConfig(
    profile_name="default",
    target_name="dev",
    profile_mapping=PostgresUserPasswordProfileMapping(
        conn_id="traffic_accidents_database",
        profile_args={"schema": "public"},
        disable_event_tracking=True,
    )
)

@dag(
    schedule=Dataset("raw_traffic_accidents"),
    start_date=datetime(2025, 1, 9),
    catchup=False,
    tags=["examples", "traffic", "pipeline"]
)
def traffic_accidents_dbt() -> None:
    DbtTaskGroup(
        group_id="transform_task_group",
        project_config=ProjectConfig(
            dbt_project_path=DBT_ROOT_PATH / "accident_accidents"
        ),
        profile_config=profile_config
    )

traffic_accidents_dbt()