from airflow.decorators import dag
from dags.operators.memory_examples.sql_to_local_pandas_operator import SQLtoLocalPandasOperator
from datetime import datetime

TABLE = "heavy_table"

@dag(
    schedule=None,
    start_date=datetime(2025, 10, 22),
    catchup=False,
    tags=["examples", "memory"],
    max_active_tasks=1,
    default_args=dict(
        retries=4
    )
)
def pandas_extraction_example():
    pandas_all = SQLtoLocalPandasOperator(
        task_id="extract_all_data",
        conn_id="warehouse",
        query="SELECT * FROM {{ params.table }}",
        params=dict(
            table=TABLE
        )
    )

    pandas_chunked = SQLtoLocalPandasOperator(
        task_id="extract_chunked_data",
        conn_id="warehouse",
        query="SELECT * FROM {{ params.table }}",
        params=dict(
            table=TABLE
        ),
        chunked=True,
        chunk_size=1_000_000
    )

pandas_extraction_example()

