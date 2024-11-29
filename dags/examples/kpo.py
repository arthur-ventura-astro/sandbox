from airflow.decorators import dag, task
from datetime import datetime

@dag(
    schedule="0 * * * *",
    start_date=datetime(2024, 11, 29),
    catchup=False,
    tags=["examples"],
)
def kpo_example():
    @task(
        retries=2
    )
    def generate_random():
        from random import randint
        return str(randint(0, 1000))

    @task.kubernetes(
        image="python:3.8-slim-buster",
        kubernetes_conn_id="cluster",
        namespace="general"
    )
    def print_random(rand):
        print(rand)

    print_random(generate_random())
kpo_example()
