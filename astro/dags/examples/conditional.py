from airflow.decorators import dag, task
from datetime import datetime
import requests

@dag(
    schedule="0 15 * * *",
    start_date=datetime(2024, 11, 6),
    catchup=False,
    tags=["examples"],
)
def conditional_example():
    @task()
    def print_environment():
        import os
        env = os.getenv("ENV", "dev")
        if env == "dev":
            print("Development")
        else:
            print("Production")

    @task
    def print_variable(var):
        print(var)

    print_environment()
    print_variable(var="{{ var.value.example_conditional }}")

conditional_example()
