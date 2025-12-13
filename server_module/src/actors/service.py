from src.actors.repository import ActorRepository
from src.actors.schemas import ActorBase


class ActorService:

    def __init__(self, repository: ActorRepository):
        self.repository = repository

    async def get_actor_by_name(self, actor_name: str) -> list[ActorBase]:
        actors = await self.repository.get_by_name(actor_name)
        return [ActorBase.model_validate(actor) for actor in actors]
