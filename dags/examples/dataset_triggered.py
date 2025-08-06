from airflow.decorators import dag, task
from airflow.datasets import Dataset
from airflow.datasets.metadata import Metadata
from datetime import datetime
import requests

meow_facts_dataset = Dataset("meow_facts")

@dag(
    schedule=meow_facts_dataset,
    start_date=datetime(2024, 11, 6),
    catchup=False,
    tags=["examples"],
)
def after_api_example():
    @task(
        retries=2
    )
    def dummy():
        print("Triggered!")

    dummy()

after_api_example()

