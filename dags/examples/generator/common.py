# Common definitions
DATA_BUCKET = "astro-sandbox-data"
GENERATOR_FILE = "generator/config.json"


# Parameter generation
def _format_params(n_dags:int, n_tasks:int):
    return [
        dict(
            number=i,
            tasks=n_tasks
        ) for i in range(n_dags)
    ]

def dynamic_params(n:int = 3):
    """
    Generate a random number of DAGs and Tasks.
    This simulates a request to an external service.
    """
    from random import randint

    n_dags = lambda d: randint(1, d)
    n_tasks = lambda t: randint(1, t)
    return _format_params(n_dags(n), n_tasks(n))

def static_params(e:str = "STATIC_GENERATOR_DAGS"):
    """
    Generate a fixed number of DAGs and Tasks based on static parameters.
    This simulates the use of environmental variables to define DAGs.
    """
    import os
    n = int(os.getenv(e, 0))

    n_dags = n
    n_tasks = n * 10
    return _format_params(n_dags, n_tasks)


# External config handling functions
def read_remote_config(conn_id:str):
    import json
    from io import StringIO
    from airflow.providers.amazon.aws.hooks.s3 import S3Hook

    s3_hook = S3Hook(aws_conn_id=conn_id)
    file_data = StringIO(
        s3_hook.read_key(
            key=GENERATOR_FILE, bucket_name=DATA_BUCKET
        )
    )
    return json.loads(
        str(file_data.read())
    ) 

def save_remote_config(config:str, conn_id:str):
    from airflow.providers.amazon.aws.hooks.s3 import S3Hook
    s3_hook = S3Hook(aws_conn_id=conn_id)
    s3_hook.load_string(
        config,
        GENERATOR_FILE,
        bucket_name=DATA_BUCKET,
        replace=True
    )
    return DATA_BUCKET, GENERATOR_FILE

# Utils
def random_processing():
    """
    Random processing to simulate a task.
    """
    from random import randint
    from time import sleep

    sleep_time = 10 * randint(1, 10)
    for _ in range(sleep_time):
        print("Processing...")
        sleep(sleep_time)
