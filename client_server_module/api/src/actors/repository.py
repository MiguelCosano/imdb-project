from sqlalchemy import nulls_last, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from src.actors.models import Actor

class ActorRepository:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_by_id(self, actor_id: str) -> Actor:
        query = select(Actor).where(Actor.nconst == actor_id)
        result = await self.session.execute(query)
        actor = result.scalar_one_or_none()

        if not actor:
            raise HTTPException(status_code=404, detail=f"Actor {actor_id} not found")

        return actor
    

    async def get_by_name(self, name: str) -> Actor:
        query = select(Actor).where(
            Actor.primary_name.ilike(f"%{name}%")
        ).order_by(
            nulls_last(Actor.birth_year),
            nulls_last(Actor.primary_profession)
        ).limit(1)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()