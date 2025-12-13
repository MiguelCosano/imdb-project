from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.actors.service import ActorService
from src.actors.repository import ActorRepository
from src.actors.schemas import ActorBase
from core.database import get_session
from core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/actors", tags=["actors"])


def get_actor_service(session: AsyncSession = Depends(get_session)) -> ActorService:
    repository = ActorRepository(session)
    return ActorService(repository)


@router.get("/search")
async def search_actors(
    name: Annotated[
        str, Query(min_length=1, description="Name of the actor to search")
    ],
    service: ActorService = Depends(get_actor_service),
) -> list[ActorBase]:
    """Search Actor by name"""
    try:
        actors = await service.get_actor_by_name(name)
        return actors
    except Exception as e:
        logger.error(f"Error searching actor by name '{name}': {e}")
        raise
