# config/datasets.py
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass(frozen=True)
class DatasetConfig:
    """Dataset configurations for IMDb ETL pipeline"""
    filename: str
    table_name: str
    columns: List[str]
    dtype_map: Dict[str, str]


ACTORS_CONFIG = DatasetConfig(
    filename="name.basics.tsv.gz",
    table_name="actors",
    columns=["nconst", "primaryName", "birthYear", "deathYear", "primaryProfession"],
    dtype_map={
        'nconst': 'object',
        'primaryName': 'object',
        'birthYear': 'Int16',
        'deathYear': 'Int16',
        'primaryProfession': 'object'
    },
)

MOVIES_CONFIG = DatasetConfig(
    filename="title.basics.tsv.gz",
    table_name="movies",
    columns=["tconst", "primaryTitle", "originalTitle", "genres"],
    dtype_map={
        'tconst': 'object',
        'primaryTitle': 'object',
        'originalTitle': 'object',
        'genres': 'object'
    },
)


DATASETS = [
    ACTORS_CONFIG,
    MOVIES_CONFIG
]
