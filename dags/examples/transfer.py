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
    def save_data():
        import numpy as np

        data = np.array([i for i in range(10)])
        np.save(f"{home_dir}/test.npy", data)

    @task(
        queue="test"
    )
    def read_data():
        import numpy as np

        data = np.load(f"{home_dir}/test.npy")
        print(data)

    save_data(read_data())

transfer_example()
