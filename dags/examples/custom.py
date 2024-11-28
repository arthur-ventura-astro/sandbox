from airflow.models import DAG
from operators.random import RandomOperator
from pendulum import datetime

with DAG(
    dag_id="custom_example",
    schedule="0 15 * * *",
    start_date=datetime(2024, 11, 6),
    catchup=False,
    tags=["examples"]
) as dag:

    random_task = RandomOperator(
        task_id="random_task",
    )

