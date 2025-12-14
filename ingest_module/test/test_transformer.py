import pandas as pd
from transform.imdb_transformer import DataTransformer
from utils.datasets_config import ACTORS_CONFIG, MOVIES_CONFIG


class TestTransformChunksMovies:
    """Test chunk transformation logic for movies."""

    def test_transform_chunks_filters_critical_nulls_actors(self):
        """Rows with critical nulls for actors should be filtered out."""
        transformer = DataTransformer()

        def sample_chunks():
            df = pd.DataFrame(
                {
                    "nconst": ["nm0000001", "nm0000002", "nm0000003"],
                    "primaryName": ["Actor1", None, "Actor3"],
                    "birthYear": [1990, 1991, None],
                    "primaryProfession": ["actor", "actress", "director"],
                    "deathYear": [None, None, None],
                }
            )
            yield df

        chunks = list(transformer.transform_chunks(sample_chunks(), ACTORS_CONFIG))

        assert len(chunks) == 1
        chunk_idx, chunk_df = chunks[0]
        assert len(chunk_df) == 1
        assert chunk_df.iloc[0]["primary_name"] == "Actor1"

    def test_transform_chunks_filters_critical_nulls_movies(self):
        """Rows with critical nulls for movies should be filtered out."""
        transformer = DataTransformer()

        def sample_chunks():
            df = pd.DataFrame(
                {
                    "tconst": ["tt0000001", "tt0000002", "tt0000003"],
                    "primaryTitle": ["Movie1", None, "Movie3"],
                    "originalTitle": ["Original1", "Original2", None],
                    "genres": ["Action", "Comedy", "Drama"],
                }
            )
            yield df

        chunks = list(transformer.transform_chunks(sample_chunks(), MOVIES_CONFIG))

        assert len(chunks) == 1
        _, chunk_df = chunks[0]
        assert len(chunk_df) == 1
        assert chunk_df.iloc[0]["primary_title"] == "Movie1"

    def test_transform_chunks_renames_columns_correctly_actors(self):
        """Columns should be renamed according to the mapping."""
        transformer = DataTransformer()

        def sample_chunks():
            df = pd.DataFrame(
                {
                    "nconst": ["nm0000001"],
                    "primaryName": ["Test Actor"],
                    "birthYear": [1990],
                    "primaryProfession": ["actor"],
                    "deathYear": [None],
                }
            )
            yield df

        chunks = list(transformer.transform_chunks(sample_chunks(), ACTORS_CONFIG))
        _, chunk_df = chunks[0]

        assert "nconst" in chunk_df.columns
        assert "primary_name" in chunk_df.columns
        assert "birth_year" in chunk_df.columns
        assert "primary_profession" in chunk_df.columns

        assert "primaryName" not in chunk_df.columns
        assert "birthYear" not in chunk_df.columns

    def test_transform_chunks_renames_columns_correctly_movies(self):
        """Columns should be renamed according to the mapping for movies."""
        transformer = DataTransformer()

        def sample_chunks():
            df = pd.DataFrame(
                {
                    "tconst": ["tt0000001"],
                    "primaryTitle": ["Test Movie"],
                    "originalTitle": ["Original Test Movie"],
                    "genres": ["Action,Drama"],
                }
            )
            yield df

        chunks = list(transformer.transform_chunks(sample_chunks(), MOVIES_CONFIG))
        _, chunk_df = chunks[0]

        assert "tconst" in chunk_df.columns
        assert "primary_title" in chunk_df.columns
        assert "original_title" in chunk_df.columns
        assert "genres" in chunk_df.columns

        assert "primaryTitle" not in chunk_df.columns
        assert "originalTitle" not in chunk_df.columns

    def test_transform_chunks_adds_is_dead_and_drops_death_year(self):
        """is_dead should be computed and death_year dropped for actors."""
        transformer = DataTransformer()

        def sample_chunks():
            df = pd.DataFrame(
                {
                    "nconst": ["nm0000001", "nm0000002"],
                    "primaryName": ["Alive Actor", "Dead Actor"],
                    "birthYear": [1990, 1950],
                    "primaryProfession": ["actor", "actor"],
                    "deathYear": [None, 2020],
                }
            )
            yield df

        chunks = list(transformer.transform_chunks(sample_chunks(), ACTORS_CONFIG))
        _, chunk_df = chunks[0]

        assert "is_dead" in chunk_df.columns
        assert "death_year" not in chunk_df.columns

        assert chunk_df.iloc[0]["is_dead"] == False
        assert chunk_df.iloc[1]["is_dead"] == True

    def test_transform_chunks_skips_empty_chunks(self):
        """Empty chunks after filtering should be skipped."""
        transformer = DataTransformer()

        def sample_chunks():
            df1 = pd.DataFrame(
                {
                    "nconst": ["nm0000001"],
                    "primaryName": ["Test"],
                    "birthYear": [1990],
                    "primaryProfession": ["actor"],
                }
            )
            df2 = pd.DataFrame(
                {
                    "nconst": [],
                    "primaryName": [],
                    "birthYear": [],
                    "primaryProfession": [],
                }
            )
            yield df1
            yield df2

        chunks = list(transformer.transform_chunks(sample_chunks(), ACTORS_CONFIG))

        assert len(chunks) == 1


class TestFilterCriticalNulls:
    """Test _filter_critical_nulls method."""

    def test_filter_critical_nulls_actors(self):
        """Rows with nulls in critical actor fields should be removed."""
        transformer = DataTransformer()

        df = pd.DataFrame(
            {
                "nconst": ["nm0000001", "nm0000002", "nm0000003", "nm0000004"],
                "primaryName": ["Actor1", None, "Actor3", "Actor4"],
                "birthYear": [1990, 1991, None, 1993],
                "primaryProfession": ["actor", "actress", "director", None],
            }
        )

        result = transformer._filter_critical_nulls(df, "actors")

        assert len(result) == 1
        assert result.iloc[0]["nconst"] == "nm0000001"

    def test_filter_critical_nulls_movies(self):
        """Rows with nulls in critical movie fields should be removed."""
        transformer = DataTransformer()

        df = pd.DataFrame(
            {
                "tconst": ["tt0000001", "tt0000002", "tt0000003", "tt0000004"],
                "primaryTitle": ["Movie1", None, "Movie3", "Movie4"],
                "originalTitle": ["Original1", "Original2", None, "Original4"],
                "genres": ["Action", "Comedy", "Drama", None],
            }
        )

        result = transformer._filter_critical_nulls(df, "movies")

        assert len(result) == 1
        assert result.iloc[0]["tconst"] == "tt0000001"
