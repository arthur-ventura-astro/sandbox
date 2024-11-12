from airflow.decorators import dag, task
from datetime import datetime
from astro import sql as aql
from astro.files import File
from astro.table import Table

import requests
import time


DATALAKE = "/usr/local/airflow/include"


@dag(
    schedule="0 15 * * *",
    start_date=datetime(2024, 11, 6),
    catchup=False,
    tags=["sdk"],
)
def sdk_el():
    @task(
        retries=2
    )
    def extract_facts(api, ds):
        import pandas as pd

        n_facts, data = 10, []
        for _ in range(n_facts):
            time.sleep(3)
            print(f"Hitting [{api}] ...")
            response = requests.get(api).json()
            data += response.get("data")

        df = pd.DataFrame(data)
        return df.to_csv(f"{DATALAKE}/etl/{ds}.csv", index=False)

    facts = extract_facts(api="{{ conn.meow_facts_api.host }}")
    
    load_facts = aql.load_file(
        task_id="load_facts",
        input_file=File(
            path=f"{DATALAKE}/etl/{{{{ds}}}}.csv"
        ),
        output_table=Table(
            name="cat_facts",
            conn_id="postgres"
        ),
        if_exists="append"
    )
    
    facts >> load_facts

sdk_el()

