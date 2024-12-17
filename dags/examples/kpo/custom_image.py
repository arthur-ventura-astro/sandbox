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
        get_logs=True,
        image_pull_policy="Always"
    )
    def print_random(rand):
        print(rand)

    @task
    def get_image():
        import os
        image = os.getenv("CUSTOM_IMAGE")
        return image

    @task.kubernetes(
        image="{{ task_instance.xcom_pull(task_ids='get_image') }}",
        namespace=NAMESPACE,
        in_cluster=True,
        get_logs=True,
        image_pull_policy="Always"
    )
    def xcom_image():
        print("xcom_image")

    print_random(generate_random())
    get_image(xcom_image())
kpo_custom_image_example()
