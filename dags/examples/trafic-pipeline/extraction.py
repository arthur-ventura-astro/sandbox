from airflow.decorators import dag, task
from datetime import datetime
from utils.database import load_data
from utils.metadata import _parse_metadata
from airflow.datasets import Dataset
from airflow.datasets.metadata import Metadata

raw_traffic_factors = Dataset("raw_traffic_factors")

@dag(
    schedule="@once",
    start_date=datetime(2025, 1, 9),
    catchup=False,
    tags=["examples", "traffic", "pipeline"],
)
def traffic_factors_el():
    @task(
        retries=2
    )
    def extract_traffic_data(dataset_url, ds):
        import pandas as pd

        df = pd.read_csv(dataset_url)
        df['ds'] = ds
        df['id'] = [i for i in range(len(df))]
        head = df.head()

        return dict(
            data=list(df.to_dict('records')),
            head=list(head.to_dict('records'))
        )

    @task(
        retries=2,
        outlets=[raw_traffic_factors]
    )
    def load_traffic_data(data, conn):
        table_name = "raw_traffic.traffic_factors"
        load_data(data.get('data'), table_name, conn)

        yield Metadata(raw_traffic_factors, _parse_metadata(data.get('head')))

    load_traffic_data(
        data=extract_traffic_data(
            dataset_url="{{ conn.traffic_factors_bucket.host }}",
            ds="{{ds}}"
        ),
        conn="traffic_factors_database"
    )

traffic_factors_el()

