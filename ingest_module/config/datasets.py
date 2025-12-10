"""Dataset configurations"""
from dataclasses import dataclass

@dataclass(frozen=True)
class DatasetConfig:
    filename: str
    table_name: str
    columns: list[str]
    dtype_map: dict

ACTORS_CONFIG = DatasetConfig(
    filename="name.basics.tsv.gz",
    table_name="actors",
    columns=["nconst", "primaryName", "birthYear", "deathYear", "primaryProfession"],
    dtype_map={'nconst': str, 'primaryName': str, 'birthYear': 'Int64', 'deathYear': 'Int64', 'primaryProfession': str}
)

MOVIES_CONFIG = DatasetConfig(
    filename="title.basics.tsv.gz",
    table_name="movies",
    columns=["tconst", "primaryTitle", "originalTitle", "genres"],
    dtype_map={'tconst': str, 'primaryTitle': str, 'originalTitle': str, 'genres': str}
)
