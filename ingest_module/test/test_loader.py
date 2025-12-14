import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from load.imdb_loader import DatabaseLoader, psql_insert_copy
from utils.datasets_config import ACTORS_CONFIG, MOVIES_CONFIG


@pytest.fixture
def mock_engine():
    """Create a mock SQLAlchemy engine."""
    return MagicMock()


@pytest.fixture
def database_loader(mock_engine):
    """Create a DatabaseLoader instance with mock engine."""
    return DatabaseLoader(engine=mock_engine)


@pytest.fixture
def sample_chunks():
    """Create sample data chunks."""
    chunk1 = pd.DataFrame(
        {
            "nconst": ["nm0000001", "nm0000002"],
            "primary_name": ["Actor1", "Actor2"],
            "birth_year": [1990, 1991],
        }
    )
    chunk2 = pd.DataFrame(
        {
            "nconst": ["nm0000003", "nm0000004"],
            "primary_name": ["Actor3", "Actor4"],
            "birth_year": [1992, 1993],
        }
    )
    return [(0, chunk1), (1, chunk2)]


class TestLoadChunks:
    """Test load_chunks method."""

    @patch("load.imdb_loader.alive_bar")
    def test_load_chunks_single_chunk(self, mock_bar, database_loader, sample_chunks):
        """Test load_chunks with single chunk."""
        mock_bar.return_value.__enter__.return_value = MagicMock()

        with patch.object(sample_chunks[0][1], "to_sql"):
            result = database_loader.load_chunks(iter(sample_chunks[:1]), ACTORS_CONFIG)

        assert result == 2

    # Ignore the warning because it is for using the mock engine and not the real one
    @pytest.mark.filterwarnings("ignore::UserWarning")
    @patch("load.imdb_loader.alive_bar")
    def test_load_chunks_multiple_chunks(
        self, mock_bar, database_loader, sample_chunks
    ):
        """Test load_chunks with multiple chunks."""
        mock_bar.return_value.__enter__.return_value = MagicMock()

        with patch.object(sample_chunks[0][1], "to_sql"):
            result = database_loader.load_chunks(iter(sample_chunks), ACTORS_CONFIG)

        assert result == 4

    @patch("load.imdb_loader.alive_bar")
    def test_load_chunks_subsequent_chunks_append_mode(self, mock_bar, database_loader, sample_chunks):
        """Test first chunk uses replace mode and subsequent chunks use append mode."""
        mock_bar.return_value.__enter__.return_value = MagicMock()
        
        with patch.object(sample_chunks[0][1], "to_sql", return_value=None) as mock_first:
            with patch.object(sample_chunks[1][1], "to_sql", return_value=None) as mock_second:
                database_loader.load_chunks(iter(sample_chunks), ACTORS_CONFIG)
        
        mock_first.assert_called_once()
        first_call_kwargs = mock_first.call_args[1]
        assert first_call_kwargs["if_exists"] == "replace"
        
        mock_second.assert_called_once()
        second_call_kwargs = mock_second.call_args[1]
        assert second_call_kwargs["if_exists"] == "append"


    @patch("load.imdb_loader.alive_bar")
    def test_load_chunks_uses_psql_insert_copy(
        self, mock_bar, database_loader, sample_chunks
    ):
        """Test load_chunks uses psql_insert_copy method."""
        mock_bar.return_value.__enter__.return_value = MagicMock()

        with patch.object(
            sample_chunks[0][1], "to_sql", return_value=None
        ) as mock_to_sql:
            database_loader.load_chunks(iter(sample_chunks[:1]), ACTORS_CONFIG)

        call_kwargs = mock_to_sql.call_args[1]
        assert call_kwargs["method"] == psql_insert_copy

    @patch("load.imdb_loader.alive_bar")
    def test_load_chunks_correct_table_name(
        self, mock_bar, database_loader, sample_chunks
    ):
        """Test load_chunks uses correct table name."""
        mock_bar.return_value.__enter__.return_value = MagicMock()

        with patch.object(
            sample_chunks[0][1], "to_sql", return_value=None
        ) as mock_to_sql:
            database_loader.load_chunks(iter(sample_chunks[:1]), ACTORS_CONFIG)

        table_name = mock_to_sql.call_args[0][0]
        assert table_name == "actors"

    @patch("load.imdb_loader.alive_bar")
    def test_load_chunks_empty_iterator(self, mock_bar, database_loader):
        """Test load_chunks with empty iterator."""
        mock_bar.return_value.__enter__.return_value = MagicMock()

        result = database_loader.load_chunks(iter([]), ACTORS_CONFIG)

        assert result == 0

    @patch("load.imdb_loader.alive_bar")
    def test_load_chunks_handles_exception(self, mock_bar, database_loader):
        """Test load_chunks handles exceptions."""
        mock_bar.return_value.__enter__.return_value = MagicMock()

        def failing_chunks():
            chunk = pd.DataFrame({"col": [1, 2]})
            yield (0, chunk)
            raise Exception("Test error")

        with patch.object(pd.DataFrame, "to_sql", side_effect=Exception("Test error")):
            with pytest.raises(Exception):
                database_loader.load_chunks(failing_chunks(), ACTORS_CONFIG)

    @patch("load.imdb_loader.alive_bar")
    def test_load_chunks_with_movies_config(self, mock_bar, database_loader):
        """Test load_chunks with movies dataset."""
        mock_bar.return_value.__enter__.return_value = MagicMock()

        chunk = pd.DataFrame(
            {
                "tconst": ["tt0000001"],
                "primary_title": ["Movie1"],
                "original_title": ["Original"],
                "genres": ["Action"],
            }
        )
        chunks = [(0, chunk)]

        with patch.object(chunk, "to_sql", return_value=None) as mock_to_sql:
            database_loader.load_chunks(iter(chunks), MOVIES_CONFIG)

        table_name = mock_to_sql.call_args[0][0]
        assert table_name == "movies"
