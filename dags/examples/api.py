from airflow.decorators import dag, task
from airflow.datasets import Dataset
from airflow.datasets.metadata import Metadata
from datetime import datetime
import requests

meow_facts_dataset = Dataset("meow_facts")

@dag(
    schedule="0 15 * * *",
    start_date=datetime(2024, 11, 6),
    catchup=False,
    tags=["examples"],
)
def api_example():
    @task(
        retries=2,
        outlets=[meow_facts_dataset]
    )
    def extract_fact(api, ds):
        print(f"Facts extraction, day {ds}.")
        print(f"Hitting [{api}] ...")
        response = requests.get(api).json()

        yield Metadata(meow_facts_dataset, response)
        return response.get("data")[0]

    @task
    def print_fact(fact):
        print("--------------------")
        print("Here is your fact...")
        lines = fact.split(".")
        for line in lines:
            print(line)

    print_fact(extract_fact(api="{{ conn.meow_facts_api.host }}", ds="{{ds}}"))

api_example()

