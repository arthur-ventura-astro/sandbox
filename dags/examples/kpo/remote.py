from airflow.decorators import dag, task
from datetime import datetime

@dag(
    schedule="0 * * * *",
    start_date=datetime(2024, 11, 29),
    catchup=False,
    tags=["examples"],
)
def kpo_remote_example():
    @task(
        retries=2
    )
    def generate_random():
        from random import randint
        return str(randint(0, 1000))

    @task.kubernetes(
        image="{{ var.value.custom_airflow }}",
        kubernetes_conn_id="cluster"
    )
    def print_random(rand):
        print(rand)

    print_random(generate_random())
kpo_remote_example()
