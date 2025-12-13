import os
import logging
from sqlalchemy import create_engine, Engine
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

def get_database_engine() -> Engine:
    """Create database engine with connection pooling"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    logging.info("Connecting to database")
    engine = create_engine(database_url)
    logging.info("Database engine created")
    return engine
