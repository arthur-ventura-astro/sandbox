from airflow.decorators import dag
from datetime import datetime
from airflow.providers.amazon.aws.operators.eks import EksPodOperator

@dag(
    schedule="0 15 * * *",
    start_date=datetime(2024, 11, 29),
    catchup=False,
    tags=["examples"],
)
def eks_remote_example():
    EksPodOperator(
        task_id="test_pod",
        pod_name="test_pod",
        cluster_name="astro-sandbox-cluster",
        namespace="default",
        image="hello-world",
        get_logs=True,
        is_delete_operator_pod=True,
        aws_conn_id='aws_default',
        startup_timeout_seconds=240
    )

eks_remote_example()
