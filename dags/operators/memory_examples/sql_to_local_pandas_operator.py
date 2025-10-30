from memory_profiler import profile

from airflow.providers.common.sql.operators.sql import BaseSQLOperator
from typing import Any, Sequence


class SQLtoLocalPandasOperator(BaseSQLOperator):
    template_fields: Sequence[str] = (
        *BaseSQLOperator.template_fields,
        "query",
        "chunked",
        "chunk_size"
    )
    template_ext = ".sql"

    def __init__(
        self,
        query: str,
        chunked: bool = False,
        chunk_size: int = 10000,
        **kwargs
    ):
        """An Airflow Operator that provides functionality to read from an database and write to an output file.

        :param sql: The SQL Query to execute
        :type sql: str, Jinja Templated, required.
        """  # noqa: 501
        self.query = query
        self.chunked = chunked
        self.chunk_size = chunk_size
        super().__init__(**kwargs)

    @profile
    def extract_all(self):
        self.log.info("Extracting Data")
        hook = self.get_db_hook()
        return hook.get_pandas_df(sql=self.query, parameters=self.params)

    @profile
    def extract_chunks(self):
        self.log.info("Extracting Data in Chunks")
        hook = self.get_db_hook()
        return hook.get_pandas_df_by_chunks(sql=self.query, chunksize=self.chunk_size)

    @profile
    def execute(self, context: 'Context') -> Any:
        if self.chunked:
            chunks = self.extract_chunks()
            for chunk_batch, df in enumerate(chunks):
                self.log.info(f"Batch[{chunk_batch}]: {len(df)} rows")
        else:
            df = self.extract_all()
            self.log.info(f"Data: {len(df)} rows")
