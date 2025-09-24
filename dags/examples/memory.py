from datetime import datetime
from airflow.decorators import dag, task
from random import randint
from memory_profiler import profile


# Utility Functions
def load_data(rows, cols):
    import pandas as pd

    data = []
    for i in range(rows):
        data.append({f"col_{c}": "x" * 1000 for c in range(cols)})

    df = pd.DataFrame(data)

    return df

@profile
def process_data(df, cols):
    total_factor = 0

    print("Factor Multiplication")
    for c in range(cols):
        col = f"col_{c}"
        factor = randint(1, 3)
        df[col] *= factor
        print(col, factor)
        total_factor += factor    

    return total_factor

def process_unoptimized(rows, cols, iterations):
    for i in range(iterations):
        df = load_data(rows, cols)
        factor = process_data(df, cols)
        print(f"[{i}] Total Factor:", factor)

def process_optimized(rows, cols, iterations):
    import gc

    for i in range(iterations):
        df = load_data(rows, cols)
        factor = process_data(df, cols)
        print(f"[{i}] Total Factor:", factor)
        del df
        gc.collect()


# Definitions
ITERATIONS = [int((i % 10) * 2) for i in range(1000)]
COLS = 10
ROWS = 10 ** 5


# DAG Configuration
@dag(
    schedule=None,
    start_date=datetime(2025, 9, 12),
    catchup=False,
    tags=["examples"],
)
def memory_consumption_example():

    @task(queue="unoptimized")
    def unoptimized_data_processing(rows, cols, iterations):
        process_unoptimized(rows, cols, iterations)

    @task(queue="optimized")
    def optimzed_data_processing(rows, cols, iterations):
        process_optimized(rows, cols, iterations)

    unoptimized_data_processing.partial(cols=COLS, rows=ROWS).expand(iterations=ITERATIONS)
    optimzed_data_processing.partial(cols=COLS, rows=ROWS).expand(iterations=ITERATIONS)


memory_consumption_example()
