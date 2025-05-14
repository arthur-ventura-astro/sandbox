from operators.kpo_sensor import KPOSensor
from airflow.configuration import conf
from airflow.models import DAG
from datetime import datetime, timedelta

NAMESPACE = conf.get("kubernetes", "NAMESPACE")

with DAG(
    dag_id="kpo_sensor_example",
    schedule=None,
    start_date=datetime(2024, 11, 29),
    catchup=False,
    tags=["examples"],
):
    default_kpo = KPOSensor(
        image="hello-world",
        name="hello-world-sensor",
        task_id="hello_world_sensor",
        in_cluster=True,
        is_delete_operator_pod=True,
        get_logs=True,
        namespace=NAMESPACE
    )
