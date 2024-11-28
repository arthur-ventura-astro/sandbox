from airflow.decorators import dag, task
from datetime import datetime
from multicron.multicron_timetable import MultiCronTimetable

@dag(
    schedule=MultiCronTimetable(
        cron_list=['*/15 * * * *', '0,15,45 12-18 * * *'],
        strategy='-'
    ),
    start_date=datetime(2024, 11, 28),
    catchup=False,
    tags=["examples"],
)
def multicron_example():
    @task(
        retries=2
    )
    def print_random():
        from random import randint
        return str(randint(0, 1000))

    print_random()
multicron_example()
