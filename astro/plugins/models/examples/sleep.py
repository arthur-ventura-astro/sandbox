from airflow.operators.bash import BashOperator

class SleepOperator(BashOperator):
    template_fields = (*BashOperator.template_fields, "sleep_time")

    def __init__(self, sleep_time, **kwargs):
        self.sleep_time = sleep_time
        super().__init__(
            bash_command=self._parse_sleep_command(),
            **kwargs
        )

    def _parse_sleep_command(self):
        return "sleep " + str(self.sleep_time)


