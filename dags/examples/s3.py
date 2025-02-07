from datetime import datetime
from airflow.decorators import dag, task

@dag(
    schedule="0 15 * * *",
    start_date=datetime(2024, 11, 6),
    catchup=False,
    tags=["examples"],
)
def s3_example():
    @task
    def save_data_to_s3():
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        s3_hook = S3Hook(aws_conn_id="aws-default")
        s3_hook.load_string(
            "Hello S3!",
            "examples/hello.txt",
            bucket_name="astro-sandbox-data",
            replace=True
        )

    save_data_to_s3()

s3_example()
