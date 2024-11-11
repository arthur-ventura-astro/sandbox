from airflow.operators.bash import BashOperator

class EchoOperator(BashOperator):
    template_fields = (*BashOperator.template_fields, "echo_msg")

    def __init__(self, echo_msg, **kwargs):
        self.echo_msg = echo_msg
        super().__init__(
            bash_command=self._parse_echo_command(),
            **kwargs
        )

    def _parse_echo_command(self):
        return 'echo "' + str(self.echo_msg) + '"'

