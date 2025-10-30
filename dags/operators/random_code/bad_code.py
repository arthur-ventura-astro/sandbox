from airflow.models import Variable, DAG
from airflow.operators.bash import BashOperator
from random import randint
from pendulum import datetime

dag = DAG(
    dag_id="bad_code_dag",
    schedule="@daily",
    start_date=datetime(2024, 11, 6),
    tags=["examples", "bad code"]
)

iterations = Variable.get("bad_code_iterations")

for iteration in range(int(iterations)):
    i = Variable.get("bad_code_iterations") * randint(0, 1000)
    task = BashOperator(
        task_id=f"rand{iteration}",
        bash_command=f'echo "Random Iterations: {i}"',
        dag=dag
    )
