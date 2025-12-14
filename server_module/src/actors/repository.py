from sqlalchemy import nulls_last, select, func, case, and_, or_
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from src.actors.models import Actor


class ActorRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_name(self, name: str) -> list[Actor]:
        ts_query = func.websearch_to_tsquery("english", name)

        exact_match = case(
            (func.lower(Actor.primary_name) == func.lower(name), 0), else_=1
        )

        query = (
            select(Actor)
            .where(Actor.search_vector.op("@@")(ts_query))
            .order_by(
                exact_match.asc(),
                func.length(Actor.primary_name).asc()
            )
        )

        result = await self.session.execute(query)
        actor = result.scalars().all()

        if not actor:
            raise HTTPException(status_code=404, detail=f"Actor '{name}' not found")

        return actor
