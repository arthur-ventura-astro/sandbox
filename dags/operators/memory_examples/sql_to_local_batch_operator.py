from memory_profiler import profile

from airflow.providers.common.sql.operators.sql import BaseSQLOperator
from typing import Any, Sequence

class SQLtoLocalBatchOperator(BaseSQLOperator):
    template_fields: Sequence[str] = (
        *BaseSQLOperator.template_fields,
        "sql"
    )
    template_ext = ".sql"

    def __init__(
        self,
        sql: str,
        **kwargs
    ):
        """An Airflow Operator that provides functionality to read from an database and write to an output file.

        :param sql: The SQL Query to execute
        :type sql: str, Jinja Templated, required.
        """  # noqa: 501
        self.sql = sql
        super().__init__(**kwargs)

    @profile
    def extract(self):
        self.log.info("Extracting Data")

        with self.get_db_hook().get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(self.sql)
                for batch in cur.get_result_batches():
                    yield batch

    @profile
    def execute(self, context: 'Context') -> Any:
        i = 0
        for batch in self.extract():
            df = batch.to_pandas()
            self.log.info(f"Batch[{i}]: {len(df)} rows")
            i += 1
        self.log.info(f"Total batches: {i}")
