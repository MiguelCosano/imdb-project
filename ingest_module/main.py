import logging
from extract.imdb_extractor import DataExtractor
from transform.imdb_transformer import DataTransformer
from load.imdb_loader import DatabaseLoader
from utils.database import get_database_engine
from utils.datasets import DatasetConfig,DATASETS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_etl_pipeline(dataset_config: DatasetConfig):
    """Run ETL for a single dataset"""
    filename = dataset_config.filename
    table_name = dataset_config.table_name
    
    logging.info(f"{'='*60}")
    logging.info(f"Processing {filename} to {table_name}")
    logging.info(f"{'='*60}")
    
    extractor = DataExtractor()
    transformer = DataTransformer()
    engine = get_database_engine()
    loader = DatabaseLoader(engine)
    
    try:
        if not extractor.should_download(filename):
            logging.info(f"Skipping {filename}")
            return
        
        logging.info("Starting pipeline")

        #extract
        raw_chunks = extractor.read_chunks(filename, dataset_config.columns, dataset_config.dtype_map)
        #transform
        transformed_chunks = transformer.transform_chunks(raw_chunks, dataset_config)
        #load
        total_rows = loader.load_chunks(transformed_chunks, dataset_config)
        
        logging.info(f"Success {filename}: {total_rows:,} rows loaded")
        return total_rows
        
    finally:
        engine.dispose()


def main():
    """Run pipeline for all datasets"""
    logging.info("Starting IMDb ETL Pipeline")
    
    for dataset_config in DATASETS:
        try:
            run_etl_pipeline(dataset_config)
        except Exception as e:
            logging.error(f"Failed {dataset_config.filename}: {e}")
            continue
    
    logging.info("Pipeline complete!!")


if __name__ == "__main__":
    main()
