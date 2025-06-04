from airflow.decorators import dag, task
from datetime import datetime
import requests, os
from airflow.models import Variable

@dag(
    schedule=None,
    start_date=datetime(2024, 11, 6),
    catchup=False,
    tags=["examples"],
)
def test_environment_manager():
    @task
    def print_generic_airflow_variable():
        var = Variable.get("specific_deployment")
        print(var)

    @task
    def print_environment_manager_airflow_variable():
        var = Variable.get("all_deployments")
        print(var)

    @task
    def print_environment_manager_os_variable():
        var = os.getenv("os_all_deployments")
        print(var)
    
    print_generic_airflow_variable()
    print_environment_manager_airflow_variable()
    print_environment_manager_os_variable()

test_environment_manager()

