from airflow.decorators import dag, task
from automated_workflows.models.storage import Storage
from datetime import datetime

@dag(
    schedule="*/5 * * * *",
    start_date=datetime(2025, 4, 3),
    catchup=False,
    tags=["Automated Workflows", "Manager"],
)
def automated_workflows_manager():
    @task(retries=2)
    def extract_workflows():
        mock_workflows = [
            dict(
                id="first_example",
                type=1,
                start="2025-04-01"
            ),
            dict(
                id="second_example",
                type=2,
                start="2025-04-02"
            )
        ]
        return mock_workflows

    @task
    def create_workflows(workflows_config: list):
        storage = Storage()
        storage.save(workflows_config)
    
    create_workflows(extract_workflows())

automated_workflows_manager()

