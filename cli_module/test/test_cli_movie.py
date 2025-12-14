import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
import requests

from imdb_cli.main import cli

@pytest.fixture
def runner():
    """Click test runner fixture following official documentation."""
    return CliRunner()

@pytest.fixture
def sample_movie_data():
    """Valid movie data matching API response."""
    return [{
        "tconst": "tt0126029",
        "primary_title": "Shrek",
        "original_title": "Shrek",
        "genres": "Animation,Comedy,Family"
    }]

@pytest.fixture
def mock_formatters():
    """Mock formatter functions to avoid import issues."""
    with patch('imdb_cli.main.format_genres', return_value="an Animation, a Comedy and a Family"), \
         patch('imdb_cli.main.plural_s', side_effect=lambda x: "s" if x != 1 else ""):
        yield

class TestMovieCommand:
    """Tests for the movie command."""

    @pytest.mark.parametrize("limit", [0, -1, -500])
    def test_invalid_movie_limit(self, runner, mock_formatters, limit):
        """Test invalid limit validation for movies."""
        result = runner.invoke(cli, ['movie', 'Shrek', f'--limit={limit}'])
        
        assert result.exit_code == 0
        assert "Error: Result number must be at least 1." in result.output

    def test_no_movies_found(self, runner, mock_formatters):
        """Test empty movie response."""
        with patch('imdb_cli.main.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = []
            mock_get.return_value = mock_response
            
            result = runner.invoke(cli, ['movie', 'NonExistentMovie'])
            
            assert result.exit_code == 0
            assert "Movie titled 'NonExistentMovie' not found." in result.output

    def test_single_movie_success(self, runner, mock_formatters, sample_movie_data):
        """Test successful single movie query."""
        with patch('imdb_cli.main.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = sample_movie_data
            mock_get.return_value = mock_response
            
            result = runner.invoke(cli, ['movie', 'Shrek'])
            
            assert result.exit_code == 0
            assert 'Found 1 movie' in result.output
            print(result.output)
            assert "Shrek, originally titled 'Shrek', is an Animation, a Comedy and a Family" in result.output

    def test_multiple_movies_with_limit(self, runner, mock_formatters, sample_movie_data):
        """Test movie limit parameter."""
        multiple_movies = sample_movie_data + [{
            "tconst": "tt0133093",
            "primary_title": "The Matrix",
            "original_title": "The Matrix",
            "genres": "Action,Sci-Fi"
        }]
        
        with patch('imdb_cli.main.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = multiple_movies
            mock_get.return_value = mock_response
            
            result = runner.invoke(cli, ['movie', 'Matrix', '--limit=1'])
            
            assert result.exit_code == 0
            assert 'Found 2 movies' in result.output
            assert 'Showing 1 movie' in result.output
            assert "The Matrix" not in result.output

    def test_movie_http_404_error(self, runner, mock_formatters):
        """Test movie 404 error handling."""
        with patch('imdb_cli.main.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
                response=mock_response
            )
            mock_get.return_value = mock_response
            
            result = runner.invoke(cli, ['movie', 'Shrek'])
            
            assert result.exit_code == 1
            assert 'Movie titled Shrek not found' in result.output

    def test_movie_http_500_error(self, runner, mock_formatters):
        """Test movie 500 error handling."""
        with patch('imdb_cli.main.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
                response=mock_response
            )
            mock_get.return_value = mock_response
            
            result = runner.invoke(cli, ['movie', 'Shrek'])
            
            assert result.exit_code == 1
            assert 'HTTP Error 500' in result.output

    def test_movie_connection_error(self, runner, mock_formatters):
        """Test movie connection error handling."""
        with patch('imdb_cli.main.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
            
            result = runner.invoke(cli, ['movie', 'Shrek'])
            
            assert result.exit_code == 1
            assert 'Connection error' in result.output

    def test_timeout_error(self, runner, mock_formatters):
        """Test movie timeout error handling."""
        with patch('imdb_cli.main.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
            
            result = runner.invoke(cli, ['movie', 'Shrek'])
            
            assert result.exit_code == 1
            assert 'Request timed out' in result.output

    def test_generic_request_exception(self, runner, mock_formatters):
        """Test generic request exception handling."""
        with patch('imdb_cli.main.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException("Request error")
            
            result = runner.invoke(cli, ['movie', 'Shrek'])
            
            assert result.exit_code == 1
            assert 'Request error' in result.output

    def test_generic_exception(self, runner, mock_formatters):
        """Test generic exception handling."""
        with patch('imdb_cli.main.requests.get') as mock_get:
            mock_get.side_effect = Exception("Generic exception")
            
            result = runner.invoke(cli, ['movie', 'Shrek'])
            
            assert result.exit_code == 1
            assert 'Unexpected error' in result.output
            