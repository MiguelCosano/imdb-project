from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from src.movies.models import Movie

class MovieRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_tile(self, title: str) -> list[Movie] | None:
        query = select(Movie).where(
            Movie.primary_title.ilike(f"%{title}%")
        )
        movie = await self.session.execute(query)
        if not Movie:
            raise HTTPException(status_code=404, detail=f"Movie {title} not found")
        return movie.scalar_one_or_none()