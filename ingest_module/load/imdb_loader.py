import logging
import csv
from io import StringIO
from sqlalchemy import Engine
from utils.datasets import DatasetConfig
from alive_progress import alive_bar
import pandas as pd
from typing import Iterator


def psql_insert_copy(table, conn, keys, data_iter):
    """
    Execute SQL statement inserting data

    Parameters
    ----------
    table : pandas.io.sql.SQLTable
    conn : sqlalchemy.engine.Engine or sqlalchemy.engine.Connection
    keys : list of str
        Column names
    data_iter : Iterable that iterates the values to be inserted
    """
    dbapi_conn = conn.connection
    with dbapi_conn.cursor() as cur:
        s_buf = StringIO()
        writer = csv.writer(s_buf)
        writer.writerows(data_iter)
        s_buf.seek(0)

        columns = ", ".join(['"{}"'.format(k) for k in keys])
        if table.schema:
            table_name = "{}.{}".format(table.schema, table.name)
        else:
            table_name = table.name

        sql = "COPY {} ({}) FROM STDIN WITH CSV".format(table_name, columns)
        cur.copy_expert(sql=sql, file=s_buf)


class DatabaseLoader:
    """Load data into the database"""

    def __init__(self, engine: Engine):
        self.engine = engine

    def load_chunks(
        self, chunks: Iterator[tuple[int, pd.DataFrame]], dataset_config: DatasetConfig
    ) -> int:
        """Load data chunks into the database table with progress tracking.

        Processes an iterator of DataFrame chunks and inserts them into the specified
        database table. The first chunk replaces any existing table, subsequent chunks
        are appended. Uses PostgreSQL COPY for optimized bulk insertion.

        Args
        ----------
            chunks: Iterator yielding tuples of (chunk_number, DataFrame) containing
                the data to be inserted.
            dataset_config: Configuration object containing the target table name
                and dataset metadata.

        Returns
        ----------
            int: Total number of rows inserted into the database across all chunks.
        """
        table_name = dataset_config.table_name
        total_rows = 0
        first_chunk = True
        chunk_count = 0

        with alive_bar(
            monitor=False, title=f"Loading {table_name}", force_tty=True
        ) as bar:
            try:
                for chunk_num, chunk_df in chunks:
                    if_exist_mode = "replace" if first_chunk else "append"

                    chunk_df.to_sql(
                        table_name,
                        self.engine,
                        if_exists=if_exist_mode,
                        index=False,
                        method=psql_insert_copy,
                    )

                    total_rows += len(chunk_df)
                    first_chunk = False
                    chunk_count += 1

                    bar.text(f"Chunk {chunk_count} | {total_rows:,} rows")
                    bar()
            except Exception as e:
                logging.error(f"Failed chunk {chunk_num}: {e}")
                raise

        logging.info(f"Total: {total_rows:,} rows loaded to {table_name}")
        return total_rows
