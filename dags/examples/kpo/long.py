from airflow.configuration import conf
from airflow.decorators import dag, task
from datetime import datetime

NAMESPACE = conf.get("kubernetes", "NAMESPACE")
ITERATIONS = (2 * 24 * 60)

def _long_loop(iter, sleep_time=60):
    from time import sleep

    print("Started")
    for i in range(iter):
        sleep(sleep_time)
        print(f"Iteration [{i}/{iter}]")
    print("Finished")


@dag(
    schedule="@once",
    start_date=datetime(2024, 11, 29),
    catchup=False,
    tags=["examples"],
)
def kpo_long_running_example():
    @task.kubernetes(
        image="python",
        namespace=NAMESPACE,
        in_cluster=True,
        get_logs=True,
        image_pull_policy="Always"
    )
    def long_running(iter):
        _long_loop(iter)

    @task.kubernetes(
        image="python",
        namespace=NAMESPACE,
        in_cluster=True,
        get_logs=True,
        image_pull_policy="Always",
        queue='isolated'
    )
    def long_running_isolated(iter):
        _long_loop(iter)

    long_running(iter=ITERATIONS)
    long_running_isolated(iter=ITERATIONS)

kpo_long_running_example()
