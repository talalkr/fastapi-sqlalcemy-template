from app.storage.db.base import db_manager


class InfraService:
    async def healthcheck(self) -> bool:
        return await db_manager.healthcheck()
