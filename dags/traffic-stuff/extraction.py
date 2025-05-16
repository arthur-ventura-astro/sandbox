from airflow.decorators import dag, task
from datetime import datetime
from utils.database import load_data
from utils.metadata import _parse_metadata
from airflow.datasets import Dataset
from airflow.datasets.metadata import Metadata

raw_traffic_accidents = Dataset("raw_traffic_accidents")

@dag(
    schedule="@once",
    start_date=datetime(2025, 1, 9),
    catchup=False,
    tags=["examples", "traffic", "pipeline"],
)
def traffic_accidents_el():
    @task(
        retries=2
    )
    def extract_traffic_data(dataset_url, ts_nodash):
        import pandas as pd

        df = pd.read_csv(dataset_url)
        df['updated_at'] = ts_nodash
        df['id'] = [i for i in range(len(df))]
        head = df.head()

        return dict(
            data=list(df.to_dict('records')),
            head=list(head.to_dict('records'))
        )

    @task(
        retries=2,
        outlets=[raw_traffic_accidents]
    )
    def load_traffic_data(data, conn):
        table_name = "raw_traffic.traffic_accidents"
        load_data(data.get('data'), table_name, conn)

        yield Metadata(raw_traffic_accidents, _parse_metadata(data.get('head')))

    load_traffic_data(
        data=extract_traffic_data(
            dataset_url="{{ conn.traffic_accidents_bucket.host }}",
            ts_nodash="{{ts_nodash}}"
        ),
        conn="traffic_accidents_database"
    )

traffic_accidents_el()

