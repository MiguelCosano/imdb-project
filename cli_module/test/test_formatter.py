import pytest
from imdb_cli.formatters import (
    format_professions,
    format_genres,
    is_dead_or_alive,
    plural_s,
)


class TestFormatProfessions:
    """Test format_professions function."""

    def test_format_professions_single_actor(self):
        """Test formatting a single profession."""
        result = format_professions("actor")
        assert "actor" in result.lower()

    def test_format_professions_multiple(self):
        """Test formatting multiple professions."""
        result = format_professions("actor,director,producer")
        assert "an actor" in result.lower()
        assert "a director" in result.lower()
        assert "a producer" in result.lower()

    @pytest.mark.parametrize("professions", [None, ""])
    def test_format_professions_none_or_empty(self, professions):
        """Test formatting None and Empty value."""
        result = format_professions(professions)
        assert "unknown" in result.lower()


class TestFormatGenres:
    """Test format_genres function."""

    def test_format_genres_single(self):
        """Test formatting a single genre."""
        result = format_genres("Drama")
        assert "a Drama" in result

    def test_format_genres_multiple(self):
        """Test formatting multiple genres."""
        result = format_genres("Drama,Action,Thriller")
        assert "a Drama" in result
        assert "an Action" in result
        assert "a Thriller" in result

    @pytest.mark.parametrize("genres", [None, ""])
    def test_format_genres_none_or_empty(self, genres):
        """Test formatting None value."""
        result = format_genres(genres)
        print(result)
        assert "an unknown genre" in result.lower()


class TestIsDeadOrAlive:
    """Test is_dead_or_alive function."""

    def test_is_dead(self):
        """Test person is dead."""
        result = is_dead_or_alive(True)
        assert result == "was"

    def test_is_alive(self):
        """Test person is alive."""
        result = is_dead_or_alive(False)
        assert result == "is"

    def test_is_dead_none(self):
        """Test with None value."""
        result = is_dead_or_alive(None)
        assert result == "is"


class TestPluralS:
    """Test plural_s function."""

    def test_plural_s_singular(self):
        """Test singular count returns empty string."""
        result = plural_s(1)
        assert result == ""

    @pytest.mark.parametrize("limit", [2, 100, 0])
    def test_plural_s_plural_or_zero(self, limit):
        """Test plural count returns 's'."""
        result = plural_s(limit)
        assert result == "s"
