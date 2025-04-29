from airflow import DAG
from automated_workflows.models.generator import Generator

generator = Generator()
generator.routine()
