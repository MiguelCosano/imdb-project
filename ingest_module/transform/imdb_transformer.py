"""Transform IMDb data"""
import logging
import pandas as pd
from config.constants import CHUNK_SIZE
from config.datasets import DatasetConfig
from alive_progress import alive_bar

class DataTransformer:
    @staticmethod
    def read_chunks(dataset_config: DatasetConfig):
        """Read TSV file in chunks and yield transformed data"""

        column_mapping = {
            'actors': {
                'nconst': 'nconst',
                'primaryName': 'primary_name',
                'birthYear': 'birth_year', 
                'deathYear': 'death_year',
                'primaryProfession': 'primary_profession'
            },
            'movies': {
                'tconst': 'tconst',
                'primaryTitle': 'primary_title',
                'originalTitle': 'original_title',
                'genres': 'genres'
            }
        }

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
                chunk = chunk.rename(columns=column_mapping[dataset_config.table_name])
                chunk = chunk.where(pd.notnull(chunk), None)

                if 'death_year' in chunk.columns:
                    chunk['is_dead'] = chunk['death_year'].notna()
                    chunk = chunk.drop(columns=['death_year'])

                yield i, chunk
                
        except FileNotFoundError as e:
            logging.error(f"File not found: {e}")
            raise
