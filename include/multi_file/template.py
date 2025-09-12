from airflow.decorators import dag
from airflow.operators.bash import BashOperator
from pendulum import datetime

dag_id = $dag_id
schedule = $schedule
bash_command = $bash_command
env_var = $env_var

@dag(
    dag_id=dag_id,
    start_date=datetime(2023, 7, 1),
    schedule=schedule,
    catchup=False,
)
def dag_from_config():
    BashOperator(
        task_id="say_hello",
        bash_command=bash_command,
        env={"ENVVAR": env_var},
    )
dag_from_config()