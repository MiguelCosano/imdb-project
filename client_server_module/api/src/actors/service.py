from src.actors.repository import ActorRepository
from src.actors.schemas import ActorBase

class ActorService:

    def __init__(self, repository: ActorRepository):
        self.repository = repository


    async def get_actor_by_id(self, actor_id: str) -> ActorBase:
        actor = await self.repository.get_by_id(actor_id)
        return ActorBase.model_validate(actor)
    
    async def get_actor_by_name(self, actor_name: str) -> ActorBase | None:
        actor = await self.repository.get_by_name(actor_name)
        if not actor:
            return None
        return ActorBase.model_validate(actor)