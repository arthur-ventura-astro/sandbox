from airflow.models import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="$DAG_ID",
    schedule="@once",
    start_date=datetime.strptime("$DAG_START", '%Y-%m-%d'),
    catchup=False,
    tags=["Automated Workflows", "Workflow A"]
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



