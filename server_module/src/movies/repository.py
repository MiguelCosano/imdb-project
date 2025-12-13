from sqlalchemy import select, func, case, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from src.movies.models import Movie


class MovieRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_title(self, title: str) -> list[Movie]:
        ts_query = func.websearch_to_tsquery("english", title)

        exact_match = case(
            (func.lower(Movie.primary_title) == func.lower(title), 0),
            else_=1,
        )

        has_nulls = case(
            (
                or_(
                    Movie.primary_title.is_(None),
                    Movie.original_title.is_(None),
                    Movie.genres.is_(None),
                ),
                1,
            ),
            else_=0,
        )

        query = (
            select(Movie)
            .where(Movie.search_vector.op("@@")(ts_query))
            .order_by(
                exact_match.asc(),
                has_nulls.asc(),
                func.length(Movie.primary_title).asc(),
            )
        )

        result = await self.session.execute(query)
        movies = result.scalars().all()

        if not movies:
            raise HTTPException(status_code=404, detail=f"Movie '{title}' not found")

        return movies
