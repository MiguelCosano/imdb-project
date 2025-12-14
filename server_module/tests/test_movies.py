from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from src.movies.repository import MovieRepository
from src.movies.models import Movie


class TestMovieRepository(IsolatedAsyncioTestCase):
    
    def setUp(self):
        """Setup before each test."""
        self.mock_session = AsyncMock()
        self.movie_repository = MovieRepository(self.mock_session)
    
    async def test_get_by_title_returns_movies(self):
        """Test successful movie search returns list of movies."""
        mock_movie1 = Movie(
            tconst="tt0111161",
            primary_title="The Shawshank Redemption",
            original_title="The Shawshank Redemption",
            genres="Drama"
        )
        
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_movie1]
        mock_result.scalars.return_value = mock_scalars
        self.mock_session.execute.return_value = mock_result
        
        result = await self.movie_repository.get_by_title("Shawshank")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].primary_title, "The Shawshank Redemption")
        self.mock_session.execute.assert_called_once()
    
    async def test_get_by_title_not_found_raises_404(self):
        """Test that non-existent movie raises HTTPException 404."""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        self.mock_session.execute.return_value = mock_result
        
        with self.assertRaises(HTTPException) as context:
            await self.movie_repository.get_by_title("NonExistentMovie")
        
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("not found", context.exception.detail.lower())
