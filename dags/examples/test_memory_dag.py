"""Test DAG with high memory usage during parsing to test profiling."""

from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

# Simulate high memory usage at module level (BAD PRACTICE!)
# Create a large list to consume memory during DAG parsing
large_data = [i for i in range(1000000)]  # ~38MB
another_large_data = {f"key_{i}": f"value_{i}" * 100 for i in range(100000)}  # More memory

# Define the DAG
with DAG(
    dag_id="test_memory_heavy_dag",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["test", "memory"],
) as dag:
    
    def process_data():
        """Task function."""
        print("Processing data...")
        return "Done"
    
    task = PythonOperator(
        task_id="process_task",
        python_callable=process_data,
    )
