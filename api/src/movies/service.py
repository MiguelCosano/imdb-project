from src.movies.repository import MovieRepository
from src.movies.schemas import MovieBase

class MovieService:

    def __init__(self, repository: MovieRepository):
        self.repository = repository
    
    async def get_movie_by_title(self, movie_title: str) -> MovieBase:
        movie = await self.repository.get_by_tile(movie_title)
        return MovieBase.model_validate(movie)