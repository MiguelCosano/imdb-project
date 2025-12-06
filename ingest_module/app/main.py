import pandas as pd
import gzip
import requests
import shutil
import logging
import os
from datetime import datetime
from dateutil.parser import parse as parsedate
from sqlalchemy import create_engine, Engine
from sys import path
import sys
from dotenv import load_dotenv
import csv
from io import StringIO

path.append(os.path.realpath("../../"))
load_dotenv()

IMDB_URL = "https://datasets.imdbws.com/"
ACTORS = "name.basics.tsv.gz"
MOVIES = "title.basics.tsv.gz"
CHUNK_SIZE = 100000

logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')

def download_if_changed(filename):
    url = f"{IMDB_URL}{filename}"
    local_path = filename
        
    resp = requests.head(url)
    remote_date = parsedate(resp.headers['Last-Modified'])
    
    if os.path.exists(local_path):
        local_date = datetime.fromtimestamp(
            os.path.getmtime(local_path)
        ).astimezone()
        
        if remote_date <= local_date:
            logging.info("No changes")
            return False
    
    logging.info(f"{filename}: Downloading...")
    r = requests.get(url)
    with open(local_path, 'wb') as f:
        f.write(r.content)
    
    logging.info(f"{filename}: Updated...")
    return True

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

        sql = 'COPY {} ({}) FROM STDIN WITH CSV'.format(
            table_name, columns)
        cur.copy_expert(sql=sql, file=s_buf)

def load_data(engine: Engine, table_name: str, selected_columns: list[str]):
    response = requests.get(f"{IMDB_URL}{ACTORS}", stream=True)
    with open("name.basics.tsv.gz", "wb") as f:
        shutil.copyfileobj(response.raw, f)

    with gzip.open("name.basics.tsv.gz", "rb") as f_in:
        with open("name.basics.tsv", "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    try:
        logging.info("Reading TSV file in chunks...")
        
        for i, chunk in enumerate(pd.read_csv(
            "name.basics.tsv",
            sep="\t", 
        usecols=selected_columns,
        chunksize=CHUNK_SIZE,
        na_values=['\\N'],
        keep_default_na=True,
        dtype={
        'nconst': str,
        'primaryName': str,
        'birthYear': 'Int64',
        'primaryProfession': str
        }
        )):
            chunk = chunk.where(pd.notnull(chunk), None)
            
            if_exist_mode = 'replace' if i == 0 else 'append'

            chunk.to_sql(
                table_name,
                engine,
                if_exists=if_exist_mode,
                index=False,
                method=psql_insert_copy
            )

            logging.info(f"Inserted chunk {i+1} ({len(chunk)} rows)")
        
        with engine.connect() as conn:
            result = pd.read_sql("SELECT COUNT(*) as total FROM actors", conn)
            logging.info(f"Total rows inserted: {result['total'][0]}")
    except Exception as e:
        logging.error(f"Exception occurred: {e}")
        raise
    finally:
        engine.dispose()
        logging.info("Database connection closed")


def connect_to_database() -> Engine:
    logging.info("Starting connection with database")
    engine = create_engine(os.getenv("DATABASE_URL"))
    logging.info(f"Database created {engine.connect}")
    return engine


def main():
    logging.info("Starting data ingestion")
    try:
        engine = connect_to_database()
    except: 
        logging.error("Error connecting to database, finalizing app...")
        sys.exit()
    load_data(engine, "actors", ["nconst", "primaryName", "birthYear", "primaryProfession"])

if __name__ == "__main__":
    main()
