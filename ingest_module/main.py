import sys
import logging
from dotenv import load_dotenv
from extract.imdb_extractor import DataExtractor
from transform.imdb_transformer import DataTransformer
from load.imdb_loader import DatabaseLoader
from utils.database import get_database_engine
from config.datasets import ACTORS_CONFIG, MOVIES_CONFIG

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_etl_pipeline(dataset_config):
    """Run the ETL pipeline for a given dataset configuration"""
    logging.info(f"Processing {dataset_config.table_name}")
    
    # Extract
    extractor = DataExtractor()
    if extractor.should_download(dataset_config.filename):
        if not extractor.download(dataset_config.filename):
            logging.error(f"Failed to download {dataset_config.filename}")
            return
    else:
        logging.info(f"Skipping {dataset_config.table_name} - no updates")
        return
    
    # Transform
    chunks = DataTransformer.read_chunks(dataset_config)
    
    # Load
    engine = get_database_engine()
    loader = DatabaseLoader(engine)
    loader.load_chunks(chunks, dataset_config)
    engine.dispose()
    
    return

def main():
    """Main entry point"""
    load_dotenv()
    logging.info("Starting ETL pipeline")
    
    try:
        run_etl_pipeline(ACTORS_CONFIG)
        run_etl_pipeline(MOVIES_CONFIG)
        
        logging.info("ETL pipeline completed successfully")
        
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
