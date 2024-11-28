from airflow.models import DAG
from airflow.operators.bash import BashOperator
from pendulum import datetime

with DAG(
    dag_id="basic_example",
    schedule="0 15 * * *",
    start_date=datetime(2024, 11, 6),
    catchup=False,
    tags=["examples"]
) as dag:

    sleep_task = BashOperator(
        task_id="sleep_task",
        bash_command="sleep 5"
    )

    echo_task = BashOperator(
        task_id="echo_task",
        bash_command='echo "Basic DAG!"'
    )

    sleep_task >> echo_task



