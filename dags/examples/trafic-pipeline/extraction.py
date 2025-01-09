from airflow.decorators import dag, task
from datetime import datetime
from utils.database import load_data

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

        df = pd.read_csv(dataset_url, index_col=0)
        df['ds'] = ds
        print(df.head())

        return df.to_dict()

    @task(
        retries=2
    )
    def load_traffic_data(data, conn):
        table_name = "raw_traffic.traffic_factors"
        load_data(data, table_name, conn)

    load_traffic_data(
        data=extract_traffic_data(
            dataset_url="{{ conn.traffic_factors_bucket.host }}",
            ds="{{ds}}"
        ),
        conn="traffic_factors_database"
    )

traffic_factors_el()

