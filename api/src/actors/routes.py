from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.actors.service import ActorService
from src.actors.repository import ActorRepository
from src.actors.schemas import ActorBase
from core.database import get_session

router = APIRouter(prefix="/actors", tags=["actors"])


def get_actor_service(session: AsyncSession = Depends(get_session)) -> ActorService:
    repository = ActorRepository(session)
    return ActorService(repository)

@router.get("/search")
async def search_actors(
    name: Annotated[str, Query(min_length=1, description="Nombre del actor a buscar")],
    service: ActorService = Depends(get_actor_service)
) -> ActorBase:
    """Search Actor by Name"""
    actor = await service.get_actor_by_name(name)
    return actor

@router.get("/{actor_id}", response_model= ActorBase)
async def get_actor_by_id(
    actor_id: str,
    service: ActorService = Depends(get_actor_service),
) -> ActorBase:
    """Get Actor by ID."""
    logger.debug(f"Fetching hero {actor_id}")
    try:
        actor = await service.get_actor_by_id(actor_id)
        logger.info(f"Retrieved actor {actor_id}")
        return actor
    except Exception as e:
        logger.error(f"Failed to fetch actor {actor_id}: {str(e)}")
        raise