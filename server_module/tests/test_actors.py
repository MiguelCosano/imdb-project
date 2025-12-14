from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from src.actors.repository import ActorRepository
from src.actors.models import Actor


class TestActorRepository(IsolatedAsyncioTestCase):
    
    def setUp(self):
        """Setup before each test."""
        self.mock_session = AsyncMock()
        self.actor_repository = ActorRepository(self.mock_session)
    
    async def test_get_by_name_returns_actors(self):
        """Test successful actor search returns list of actors."""
        mock_actor1 = Actor(
            nconst=1,
            primary_name="Tom Hanks",
            birth_year=1956,
            primary_profession="actor,producer"
        )
        
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_actor1]
        mock_result.scalars.return_value = mock_scalars
        self.mock_session.execute.return_value = mock_result
        
        result = await self.actor_repository.get_by_name("Tom")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].primary_name, "Tom Hanks")
        self.mock_session.execute.assert_called_once()
    
    async def test_get_by_name_not_found_raises_404(self):
        """Test that non-existent actor raises HTTPException 404."""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        self.mock_session.execute.return_value = mock_result
        
        with self.assertRaises(HTTPException) as context:
            await self.actor_repository.get_by_name("NonExistentActor")
        
        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("not found", context.exception.detail.lower())
