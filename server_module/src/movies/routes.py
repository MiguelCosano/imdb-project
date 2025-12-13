from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.movies.service import MovieService
from src.movies.repository import MovieRepository
from src.movies.schemas import MovieBase
from core.database import get_session
from core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/movies", tags=["movies"])


def get_movie_service(session: AsyncSession = Depends(get_session)) -> MovieService:
    repository = MovieRepository(session)
    return MovieService(repository)


@router.get("/search")
async def search_movie(
    title: Annotated[
        str, Query(min_length=1, description="Title of the movie to search")
    ],
    service: MovieService = Depends(get_movie_service),
) -> list[MovieBase]:
    """Search Movie by title"""
    try:
        movies = await service.get_movie_by_title(title)
        return movies
    except Exception as e:
        logger.error(f"Error searching movie by title '{title}': {e}")
        raise
