from airflow.configuration import conf
from airflow.decorators import dag, task
from datetime import datetime

NAMESPACE = conf.get("kubernetes", "NAMESPACE")

@dag(
    schedule="@once",
    start_date=datetime(2024, 11, 29),
    catchup=False,
    tags=["examples"],
)
def kpo_custom_image_example():
    @task(
        retries=2
    )
    def generate_random():
        from random import randint
        return str(randint(0, 1000))

    @task.kubernetes(
        image="{{ var.value.custom_image }}",
        namespace=NAMESPACE,
        in_cluster=True,
        get_logs=True
    )
    def print_random(rand):
        print(rand)

    print_random(generate_random())
kpo_custom_image_example()
