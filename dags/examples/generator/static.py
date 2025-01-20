from datetime import datetime
from airflow.decorators import dag, task
from examples.generator.common import (
    static_params,
    random_processing
)

# Generate Static Config DAGs
static_config = static_params()
for dag_config in static_config:
    dag_id = f"static_dag_n{dag_config['number']}"

    @dag(
        dag_id=dag_id,
        schedule="0 16 * * *",
        start_date=datetime(2025, 1, 17),
        catchup=False,
        tags=["static", "generator"]
    )
    def static_dag():
        for t in range(dag_config['tasks']):
            @task(
                task_id=f"task_n{t}"
            )
            def static_task():
                random_processing()

            static_task()
    static_dag()

