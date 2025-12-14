import pytest
import pandas as pd
import requests
from unittest.mock import Mock, patch, MagicMock
from extract.imdb_extractor import DataExtractor

@patch("extract.imdb_extractor.pd.read_csv")
@patch("extract.imdb_extractor.save_metadata")
class TestReadChunks:
    """Test read_chunks method."""

    def test_read_chunks_yields_dataframes(self, mock_save_metadata, mock_read_csv):
        """Test read_chunks yields pandas DataFrames."""
        test_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mock_read_csv.return_value = iter([test_df])

        extractor = DataExtractor()

        with patch.object(extractor, "_get_file_metadata", return_value="etag123"):
            chunks = list(
                extractor.read_chunks(
                    "test.tsv.gz", ["col1", "col2"], {"col1": int, "col2": int}
                )
            )

        assert len(chunks) == 1
        assert isinstance(chunks[0], pd.DataFrame)

    def test_read_chunks_calls_save_metadata(self, mock_save_metadata, mock_read_csv):
        """Test read_chunks saves metadata after streaming."""
        mock_read_csv.return_value = iter([])
        extractor = DataExtractor()

        with patch.object(extractor, "_get_file_metadata", return_value="etag456"):
            list(extractor.read_chunks("test.tsv.gz", [], {}))

        mock_save_metadata.assert_called()

    def test_read_chunks_handles_exception(self, mock_save_metadata, mock_read_csv):
        """Test read_chunks handles exceptions properly."""
        mock_read_csv.side_effect = Exception("Test error")
        extractor = DataExtractor()

        with patch.object(extractor, "_get_file_metadata", return_value="etag123"):
            with pytest.raises(Exception):
                list(extractor.read_chunks("test.tsv.gz", [], {}))


class TestGetFileMetadata:
    """Test _get_file_metadata method."""

    @patch("extract.imdb_extractor.requests.head")
    def test_get_file_metadata_returns_etag(self, mock_head):
        """Test _get_file_metadata returns ETag from response."""
        mock_response = MagicMock()
        mock_response.headers = {"ETag": "test-etag-123"}
        mock_head.return_value = mock_response

        extractor = DataExtractor()
        result = extractor._get_file_metadata("https://example.com/test.tsv.gz")

        assert result == "test-etag-123"

    @patch("extract.imdb_extractor.requests.head")
    def test_get_file_metadata_timeout(self, mock_head):
        """Test _get_file_metadata handles timeout."""
        mock_head.side_effect = requests.Timeout("Timeout")

        extractor = DataExtractor()
        result = extractor._get_file_metadata("https://example.com/test.tsv.gz")

        assert result == (None, 0)

    @patch("extract.imdb_extractor.requests.head")
    def test_get_file_metadata_http_error(self, mock_head):
        """Test _get_file_metadata handles HTTP errors."""
        mock_head.side_effect = requests.HTTPError("404 Not Found")

        extractor = DataExtractor()
        result = extractor._get_file_metadata("https://example.com/test.tsv.gz")

        assert result == (None, 0)
