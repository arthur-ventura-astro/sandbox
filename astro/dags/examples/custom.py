from airflow.models import DAG
from plugins.models.examples.sleep import SleepOperator
from plugins.models.examples.echo import EchoOperator
from pendulum import datetime

with DAG(
    dag_id="custom_example",
    schedule="0 15 * * *",
    start_date=datetime(2024, 11, 6),
    tags=["examples"]
) as dag:

    sleep_task = SleepOperator(
        task_id="sleep_task",
        sleep_time=5
    )

    echo_task = EchoOperator(
        task_id="echo_task",
        echo_msg="Basic DAG!"
    )

    sleep_task >> echo_task

