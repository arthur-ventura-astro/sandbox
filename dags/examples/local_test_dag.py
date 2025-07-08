from airflow.decorators import dag, task
from datetime import datetime
import os
from airflow.models import Variable

testing = Variable.get("testing")

@dag(
    schedule=None,
    start_date=datetime(2024, 11, 6),
    catchup=False,
    tags=["examples"],
)
def local_test_dag():
    @task
    def print_variable():
        another_testing = Variable.get("another_testing")
        print(another_testing, testing)
    
    print_variable()

local_test_dag()