import os
from airflow.models import DAG
from airflow.operators.python import PythonOperator
from pendulum import datetime

def download_from_s3(key: str, bucket_name: str, local_path: str) -> str:
    from airflow.providers.amazon.aws.hooks.s3 import S3Hook

    hook = S3Hook('s3_conn')
    file_name = hook.download_file(key=key, bucket_name=bucket_name, local_path=local_path)
    return file_name
    
    
with DAG(
    dag_id="test_s3_connection",
    schedule="0 15 * * *",
    start_date=datetime(2025, 7, 1),
    catchup=False,
    tags=["cosmos", "s3"]    
) as dag:
    # Download a file
    task_download_from_s3 = PythonOperator(
        task_id='download_from_s3',
        python_callable=download_from_s3,
        op_kwargs={
            'key': '...',
            'bucket_name': 'bds-airflow-bucket',
            'local_path': '/Users/dradecic/airflow/data/'
        }
    )