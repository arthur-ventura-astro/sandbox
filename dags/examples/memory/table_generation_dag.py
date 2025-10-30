from airflow.decorators import dag, task
from datetime import datetime

TABLE = "heavy_table"
BATCHES = [10_000 for _ in range(100)]

@dag(
    schedule=None,
    start_date=datetime(2025, 10, 22),
    catchup=False,
    tags=["examples", "memory"],
    default_args=dict(
        retries=4
    )
)
def generate_keavy_data_example():
    @task
    def generate_random_data(batch, ts_nodash):
        from random import randint
        return [
            dict(payload="x".join([str(randint(0, 10)) for _ in range(100)]), dt=ts_nodash) for _ in range(batch)
        ]

    @task.snowpark(
        task_id="load_data",
        snowflake_conn_id="warehouse",
        pool="snowflake"
    )
    def load_data(data: list[dict], session):
        if data:
            df = session.create_dataframe(data)
            df.write.save_as_table(TABLE, mode="append")

    batch_data = generate_random_data.expand(batch=BATCHES)
    load_data.expand(data=batch_data)

generate_keavy_data_example()

