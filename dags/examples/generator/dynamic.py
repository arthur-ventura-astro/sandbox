from datetime import datetime
from airflow.decorators import dag, task
from examples.generator.common import (
    read_remote_config,
    random_processing
)

# Generate Dynamic Config DAGs
dynamic_config = read_remote_config("aws-default")
for dag_config in dynamic_config:
    dag_id = f"dynamic_dag_n{dag_config['number']}"

    @dag(
        dag_id=dag_id,
        schedule="0 16 * * *",
        start_date=datetime(2025, 1, 17),
        catchup=False,
        tags=["dynamic", "generator"]
    )
    def dynamic_dag():
        for t in range(dag_config['tasks']):
            @task(
                task_id=f"task_n{t}"
            )
            def dynamic_task():
                random_processing()

            dynamic_task()
    dynamic_dag()
