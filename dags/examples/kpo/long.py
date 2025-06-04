from airflow.configuration import conf
from airflow.decorators import dag, task
from datetime import datetime

NAMESPACE = conf.get("kubernetes", "NAMESPACE")
ITERATIONS = (2 * 24 * 60)

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
        get_logs=True
    )
    def long_running(iter, sleep_time=60):
        from time import sleep

        print("Started")
        for i in range(iter):
            sleep(sleep_time)
            print(f"Iteration [{i}/{iter}]")
        print("Finished")

    @task(
        queue='isolated'
    )
    def long_running_isolated(iter, sleep_time=60):
        from time import sleep

        print("Started")
        for i in range(iter):
            sleep(sleep_time)
            print(f"Iteration [{i}/{iter}]")
        print("Finished")

    long_running(iter=ITERATIONS)
    long_running_isolated(iter=ITERATIONS)

kpo_long_running_example()
