from datetime import datetime
from airflow.decorators import dag, task
from airflow.datasets import Dataset
from airflow.datasets.metadata import Metadata
from examples.generator.common import (
    dynamic_params,
    save_remote_config
)

generator_dataset = Dataset("dynamic_generator_dataset")

@dag(
    schedule="0 15 * * *",
    start_date=datetime(2025, 1, 17),
    catchup=False,
    tags=["examples", "generator"],
)
def dynamic_generator_params():
    @task
    def get_params():
        return dynamic_params()

    @task(
        outlets=[generator_dataset]
    )
    def save_params(data, conn_id="aws_default"):
        data_serializable = str(data).replace("'", '"')
        _, config_file = save_remote_config(data_serializable, conn_id)

        metadata = dict(
            params=data,
            config_file=config_file
        )
        yield Metadata(generator_dataset, metadata)

    save_params(
        data=get_params()
    )

dynamic_generator_params()

