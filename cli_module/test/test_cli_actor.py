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
def mock_formatters():
    """Mock formatter functions to avoid import issues."""
    with patch('imdb_cli.main.format_professions', return_value="profession: actor"), \
         patch('imdb_cli.main.is_dead_or_alive', return_value="has"):
        yield


@pytest.fixture
def sample_actor_data():
    """Valid actor data matching API response."""
    return [{
        "nconst": "nm0000158",
        "primary_name": "Tom Hanks",
        "birth_year": 1956,
        "primary_profession": "actor",
        "is_dead": False
    }]


class TestActorCommand:
    """Tests for the actor command."""

    @pytest.mark.parametrize("limit", [0, -1, -500])
    def test_invalid_limit_validation(self, runner, mock_formatters, limit):
        """Test that invalid limit values are caught early."""
        result = runner.invoke(cli, ['actor', 'Tom Hanks', f'--limit={limit}'])
        
        assert result.exit_code == 0
        assert "Error: Result number must be at least 1." in result.output

    def test_no_actors_found(self, runner, mock_formatters):
        """Test handling of empty API response."""
        with patch('imdb_cli.main.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = []
            mock_get.return_value = mock_response
            
            result = runner.invoke(cli, ['actor', 'NonExistentActor'])
            
            assert result.exit_code == 0
            assert "Actor named 'NonExistentActor' not found." in result.output

    def test_single_actor_success(self, runner, mock_formatters, sample_actor_data):
        """Test successful single actor query."""
        with patch('imdb_cli.main.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = sample_actor_data
            mock_get.return_value = mock_response
            
            result = runner.invoke(cli, ['actor', 'Tom Hanks'])
            
            assert result.exit_code == 0
            assert 'Found 1 actor' in result.output
            assert "Showing 1 actor." in result.output
            assert 'Tom Hanks was born in 1956 and has the following profession: actor' in result.output

    def test_multiple_actors_with_limit(self, runner, mock_formatters, sample_actor_data):
        """Test limit parameter with multiple results."""
        multiple_actors = sample_actor_data + [{
            "nconst": "nm0000602",
            "primary_name": "Robert De Niro",
            "birth_year": 1943,
            "primary_profession": "actor,director",
            "is_dead": False
        }]
        
        with patch('imdb_cli.main.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = multiple_actors
            mock_get.return_value = mock_response
            
            result = runner.invoke(cli, ['actor', 'Tom', '--limit=1'])
            
            assert result.exit_code == 0
            assert 'Found 2 actors' in result.output
            assert 'Showing 1 actor' in result.output
            assert 'Tom Hanks' in result.output
            assert 'Robert De Niro' not in result.output

    def test_http_404_error(self, runner, mock_formatters):
        """Test HTTP 404 error handling."""
        with patch('imdb_cli.main.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
                response=mock_response
            )
            mock_get.return_value = mock_response
            
            result = runner.invoke(cli, ['actor', 'TestActor'])
            
            assert result.exit_code == 1  # Click.Abort()
            assert 'Actor named TestActor not found' in result.output

    def test_http_500_error(self, runner, mock_formatters):
        """Test HTTP 500 error handling."""
        with patch('imdb_cli.main.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
                response=mock_response
            )
            mock_get.return_value = mock_response
            
            result = runner.invoke(cli, ['actor', 'TestActor'])
            
            assert result.exit_code == 1
            assert 'HTTP Error 500' in result.output

    def test_connection_error(self, runner, mock_formatters):
        """Test connection error handling."""
        with patch('imdb_cli.main.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
            
            result = runner.invoke(cli, ['actor', 'Tom Hanks'])
            
            assert result.exit_code == 1
            assert 'Connection error' in result.output

    def test_timeout_error(self, runner, mock_formatters):
        """Test timeout error handling."""
        with patch('imdb_cli.main.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
            
            result = runner.invoke(cli, ['actor', 'Tom Hanks'])
            
            assert result.exit_code == 1
            assert 'Request timed out' in result.output

    def test_generic_request_exception(self, runner, mock_formatters):
        """Test generic request exception handling."""
        with patch('imdb_cli.main.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException("Request error")
            
            result = runner.invoke(cli, ['actor', 'Tom Hanks'])
            
            assert result.exit_code == 1
            assert 'Request error' in result.output

    def test_generic_exception(self, runner, mock_formatters):
         """Test generic exception handling."""
         with patch('imdb_cli.main.requests.get') as mock_get:
            mock_get.side_effect = Exception("Generic exception")
            
            result = runner.invoke(cli, ['actor', 'Tom Hanks'])
            
            assert result.exit_code == 1
            assert 'Unexpected error' in result.output
            