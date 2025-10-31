"""Test DAG for operator whitelist/blacklist validation."""

from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator

# Define the DAG
with DAG(
    dag_id="test_operator_validation",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["test", "operators"],
) as dag:
    
    # Allowed operator - PythonOperator
    python_task = PythonOperator(
        task_id="python_task",
        python_callable=lambda: print("Python task"),
    )
    
    # Allowed operator - BashOperator
    bash_task = BashOperator(
        task_id="bash_task",
        bash_command="echo 'Bash task'",
    )
    
    # Allowed operator - EmailOperator
    email_task = EmailOperator(
        task_id="email_task",
        to="test@example.com",
        subject="Test Email",
        html_content="<p>Test</p>",
    )
    
    python_task >> bash_task >> email_task
