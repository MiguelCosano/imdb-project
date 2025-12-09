"""Load data into database"""
import logging
import csv
from io import StringIO
from sqlalchemy import Engine
from config.datasets import DatasetConfig
from alive_progress import alive_bar

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

        columns = ', '.join(['"{}"'.format(k) for k in keys])
        if table.schema:
            table_name = '{}.{}'.format(table.schema, table.name)
        else:
            table_name = table.name

        sql = 'COPY {} ({}) FROM STDIN WITH CSV'.format(table_name, columns)
        cur.copy_expert(sql=sql, file=s_buf)

class DatabaseLoader:
    def __init__(self, engine: Engine):
        self.engine = engine
        
    def load_chunks(self, chunks, dataset_config: DatasetConfig):
        """Load data chunks into database"""
        total_rows = 0
        
        chunks_list = list(chunks)
        
        with alive_bar(len(chunks_list), title=f"Loading {dataset_config.table_name}", force_tty=True) as bar:
            for i, chunk in chunks_list:
                if_exist_mode = 'replace' if i == 0 else 'append'
            
                chunk.to_sql(
                    dataset_config.table_name,
                    self.engine,
                    if_exists=if_exist_mode,
                    index=False,
                    method=psql_insert_copy
                )
                
                total_rows += len(chunk)
                bar()
        
        return total_rows