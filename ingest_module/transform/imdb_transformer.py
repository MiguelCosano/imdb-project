import logging
import pandas as pd
from typing import Iterator
from utils.datasets_config import DatasetConfig


class DataTransformer:
    """Transform and clean IMDb data"""

    def transform_chunks(
        self, raw_chunks: Iterator[pd.DataFrame], dataset_config: DatasetConfig
    ) -> Iterator[tuple[int, pd.DataFrame]]:
        """
        Transform raw chunks with data quality filters

        Args
        ----------
            raw_chunks: Iterator of raw DataFrames from DataExtractor
            dataset_config: Dataset configuration

        Yields
        ----------
            Tuple of (chunk_number, transformed_dataframe)
        """
        table_name = dataset_config.table_name
        mapping = dataset_config.mapping

        for i, chunk in enumerate(raw_chunks):

            if dataset_config.columns:
                available_cols = [
                    col for col in dataset_config.columns if col in chunk.columns
                ]
                chunk = chunk[available_cols].copy()

            if chunk.empty:
                logging.debug(f"Chunk {i} empty after filtering")
                continue

            chunk = self._filter_critical_nulls(chunk, table_name)

            chunk = chunk.rename(columns=mapping)

            chunk = chunk.where(pd.notnull(chunk), None)

            if table_name == "actors" and "death_year" in chunk.columns:
                chunk["is_dead"] = chunk["death_year"].notna()
                chunk = chunk.drop(columns=["death_year"])

            yield i, chunk

    def _filter_critical_nulls(
        self, chunk: pd.DataFrame, table_name: str
    ) -> pd.DataFrame:
        """Filter rows where critical fields are null"""
        if table_name == "actors":
            chunk = chunk[
                chunk["primaryName"].notna()
                & chunk["birthYear"].notna()
                & chunk["primaryProfession"].notna()
            ]

        elif table_name == "movies":
            chunk = chunk[
                chunk["primaryTitle"].notna()
                & chunk["originalTitle"].notna()
                & chunk["genres"].notna()
            ]

        return chunk
