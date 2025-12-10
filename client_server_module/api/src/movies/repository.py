from sqlalchemy import nulls_last, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from src.movies.models import Movie

class MovieRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_title(self, title: str) -> Movie:
        query = select(Movie).where(
            Movie.primary_title.ilike(f"%{title}%")
        ).order_by(
            nulls_last(Movie.original_title),
            nulls_last(Movie.genres)
        ).limit(1)
        result = await self.session.execute(query)
        movie = result.scalar_one_or_none()
        if not Movie:
            raise HTTPException(status_code=404, detail=f"Movie {title} not found")
        return movie