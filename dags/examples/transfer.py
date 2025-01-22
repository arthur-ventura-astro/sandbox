import os
from datetime import datetime
from pathlib import Path
from airflow.decorators import dag, task

home_dir = Path(os.getenv("AIRFLOW_HOME"))

@dag(
    schedule="0 15 * * *",
    start_date=datetime(2024, 11, 6),
    catchup=False,
    tags=["examples"],
)
def transfer_example():
    @task(
        queue="test"
    )
    def save_to_filesystem():
        import numpy as np

        data = np.array([i for i in range(10)])
        np.save(f"{home_dir}/test.npy", data)

    @task(
        queue="test"
    )
    def read_from_filesystem():
        import numpy as np

        data = np.load(f"{home_dir}/test.npy")
        print(data)

    @task
    def save_to_xcom_small():
        data = {"key": "x" * 10}
        return data

    @task
    def read_from_xcom_small(data):
        print(f"Size of object: {data.__sizeof__()}")

    @task
    def save_to_xcom_large():
        data = {f"key{i}": "x" * 100 for i in range(100)}
        return data

    @task
    def read_from_xcom_large(data):
        print(f"Size of object: {data.__sizeof__()}")

    save_to_filesystem() >> read_from_filesystem()
    read_from_xcom_small(save_to_xcom_small())
    read_from_xcom_large(save_to_xcom_large())

transfer_example()
