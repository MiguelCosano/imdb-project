"""Transform IMDb data"""
import logging
import pandas as pd
from config.constants import CHUNK_SIZE
from config.datasets import DatasetConfig

class DataTransformer:
    @staticmethod
    def read_chunks(dataset_config: DatasetConfig):
        """Read TSV file in chunks and yield transformed data"""
        tsv_file = dataset_config.filename
        
        try:
            for i, chunk in enumerate(pd.read_csv(
                f"./data/{tsv_file}",
                sep="\t",
                usecols=dataset_config.columns,
                chunksize=CHUNK_SIZE,
                na_values=['\\N'],
                keep_default_na=True,
                dtype=dataset_config.dtype_map
            )):
                chunk = chunk.where(pd.notnull(chunk), None)
                yield i, chunk
                
        except FileNotFoundError as e:
            logging.error(f"File not found: {e}")
            raise
