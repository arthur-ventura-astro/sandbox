from airflow.operators.bash import BashOperator

class RandomOperator(BashOperator):
    def __init__(self, **kwargs):
        super().__init__(
            bash_command=self._parse_random_command(),
            **kwargs
        )

    def _parse_random_command(self):
        import random
        return 'echo "Random Number: ' + str(random.randint(0, 1000)) + '"'
