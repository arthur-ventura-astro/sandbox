from airflow.decorators import dag
from dags.operators.memory_examples.sql_to_local_batch_operator import SQLtoLocalBatchOperator
from datetime import datetime

TABLE = "heavy_table"

@dag(
    schedule=None,
    start_date=datetime(2025, 10, 22),
    catchup=False,
    tags=["examples", "memory"],
    default_args=dict(
        retries=4
    )
)
def chunked_extraction_example():
    SQLtoLocalBatchOperator(
        task_id="extract_data",
        conn_id="warehouse",
        sql="SELECT * FROM {{ params.table }}",
        params=dict(
            table=TABLE
        )
    )

chunked_extraction_example()

