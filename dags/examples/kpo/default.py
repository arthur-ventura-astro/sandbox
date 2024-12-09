from airflow.configuration import conf
from airflow.models import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import (
    KubernetesPodOperator,
)
from datetime import datetime

NAMESPACE = conf.get("kubernetes", "NAMESPACE")

with DAG(
    dag_id="kpo_default_example",
    schedule="0 15 * * *",
    start_date=datetime(2024, 11, 29),
    catchup=False,
    tags=["examples"],
):
    default_kpo = KubernetesPodOperator(
        image="hello-world",
        name="kpo-hello-world",
        task_id="hello_world",
        in_cluster=True,
        is_delete_operator_pod=True,
        get_logs=True,
        namespace=NAMESPACE
    )
