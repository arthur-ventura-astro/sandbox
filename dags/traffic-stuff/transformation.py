import os
from datetime import datetime
from pathlib import Path

from airflow.decorators import dag

from cosmos import DbtTaskGroup, ProfileConfig, ProjectConfig, RenderConfig
from cosmos.profiles import PostgresUserPasswordProfileMapping
from airflow.datasets import Dataset

DBT_ROOT_PATH = Path(os.getenv("AIRFLOW_HOME")) / "dbt"


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
def traffic_accidents_incremental_dbt() -> None:
    DbtTaskGroup(
        group_id="transform_task_group",
        project_config=ProjectConfig(
            dbt_project_path=DBT_ROOT_PATH / "accident_factors"
        ),
        profile_config=profile_config
    )

@dag(
    schedule=None,
    start_date=datetime(2025, 1, 9),
    catchup=False,
    tags=["examples", "traffic", "pipeline"]
)
def traffic_accidents_full_refresh_dbt() -> None:
    DbtTaskGroup(
        group_id="transform_task_group",
        project_config=ProjectConfig(
            dbt_project_path=DBT_ROOT_PATH / "accident_factors"
        ),
        render_config=RenderConfig(
            select=["int_urban_traffic","int_rural_traffic"],
        ),
        operator_args={
            "full_refresh": True
        },
        profile_config=profile_config
    )

traffic_accidents_incremental_dbt()
traffic_accidents_full_refresh_dbt()