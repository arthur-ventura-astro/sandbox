import polars as pl
from polars.exceptions import NoDataError


def _retrieve_conn_uri(connection):
    from airflow.hooks.base_hook import BaseHook

    conn_uri = BaseHook.get_connection(connection).get_uri()
    return conn_uri.replace("postgres://", "postgresql+psycopg2://")


def _build_connection(connection):
    from sqlalchemy import create_engine
    conn_uri = _retrieve_conn_uri(connection)
    return create_engine(conn_uri)


def load_data(data, table, conn_id):
    try:
        df = pl.DataFrame(data)
    except NoDataError:
        print("No data. Skipping load.")
        return True

    conn = _build_connection(conn_id)
    df.write_database(
        table_name=table,
        connection=conn.connect(),
        if_table_exists='append'
    )
    print(f"Successful Data Insert: table ({table}), rows ({len(df)}).")