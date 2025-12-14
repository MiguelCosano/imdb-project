import pytest
import requests
from unittest.mock import patch, MagicMock
from utils.metadata import load_metadata, save_metadata, should_reload, get_metadata_info


@pytest.fixture
def temp_metadata_file(tmp_path, monkeypatch):
    """Create temporary metadata file"""
    metadata_file = tmp_path / "metadata.json"
    
    import utils.metadata as metadata_module
    monkeypatch.setattr(metadata_module, 'METADATA_FILE', metadata_file)
    
    return metadata_file


def test_save_and_load_metadata(temp_metadata_file):
    """Test saving and loading metadata"""
    save_metadata("test.tsv.gz", "etag123")
    
    metadata = load_metadata()
    
    assert "test.tsv.gz" in metadata
    assert metadata["test.tsv.gz"]["etag"] == "etag123"


def test_should_reload_etag_match(temp_metadata_file):
    """Test should_reload returns False when ETags match"""
    stored_metadata = {
        "test.tsv.gz": {
            "etag": "etag123"
        }
    }
    url = "https://example.com/test.tsv.gz"
    
    mock_response = MagicMock()
    mock_response.headers = {"ETag": "etag123"}
    
    with patch("utils.metadata.requests.head", return_value=mock_response):
        result = should_reload(stored_metadata, url)
    
    assert result is False


def test_should_reload_etag_mismatch(temp_metadata_file):
    """Test should_reload returns True when ETags don't match"""
    stored_metadata = {
        "test.tsv.gz": {
            "etag": "etag123"
        }
    }
    url = "https://example.com/test.tsv.gz"
    
    mock_response = MagicMock()
    mock_response.headers = {"ETag": "etag456"}
    
    with patch("utils.metadata.requests.head", return_value=mock_response):
        result = should_reload(stored_metadata, url)
    
    assert result is True


def test_should_reload_no_metadata(temp_metadata_file):
    """Test should_reload returns True when no metadata exists"""
    stored_metadata = {}
    url = "https://example.com/test.tsv.gz"
    
    result = should_reload(stored_metadata, url)
    
    assert result


def test_save_metadata_creates_directory(tmp_path, monkeypatch):
    """Test that save_metadata creates directory if not exists"""
    metadata_file = tmp_path / "nested" / "dir" / "metadata.json"
    
    import utils.metadata as metadata_module
    monkeypatch.setattr(metadata_module, 'METADATA_FILE', metadata_file)
    
    save_metadata("test.tsv.gz", "etag456")
    
    assert metadata_file.exists()
    assert metadata_file.parent.exists()


def test_should_reload_request_exception(temp_metadata_file):
    """Test should_reload returns True on request exception"""
    stored_metadata = {
        "test.tsv.gz": {
            "etag": "etag123"
        }
    }
    url = "https://example.com/test.tsv.gz"
    
    with patch("utils.metadata.requests.head", side_effect=requests.RequestException("Network error")):
        result = should_reload(stored_metadata, url)
    
    assert result is True


def test_load_metadata_file_not_exists(temp_metadata_file):
    """Test loading metadata when file doesn't exist"""
    metadata = load_metadata()
    
    assert not metadata


def test_save_metadata_overwrites_existing(temp_metadata_file):
    """Test save_metadata overwrites existing entry"""
    save_metadata("test.tsv.gz", "etag1")
    save_metadata("test.tsv.gz", "etag2")
    
    metadata = load_metadata()
    
    assert metadata["test.tsv.gz"]["etag"] == "etag2"
