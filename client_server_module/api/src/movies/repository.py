from sqlalchemy import nulls_last, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from src.movies.models import Movie

class MovieRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_title(self, title: str) -> Movie | None:
        query = select(Movie).where(
            Movie.primary_title.ilike(f"%{title}%")
        ).order_by(
            nulls_last(Movie.original_title),
            nulls_last(Movie.genres)
        ).limit(1)
        movie = await self.session.execute(query)
        if not Movie:
            raise HTTPException(status_code=404, detail=f"Movie {title} not found")
        return movie.scalar_one_or_none()