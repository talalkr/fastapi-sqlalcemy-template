from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.exceptions import DatabaseNotConnectedException
from app.settings.db import DatabaseSettings


class ConnectionManager:
    def __init__(self, settings: DatabaseSettings) -> None:
        self.settings = settings
        self._engine: AsyncEngine | None = None

    def connect(self) -> None:
        if self._engine is None:
            self._engine = create_async_engine(self.settings.build_dsn())

    @property
    def engine(self) -> AsyncEngine:
        if self._engine is None:
            raise DatabaseNotConnectedException("DB Engine is not created")
        return self._engine

    async def close(self) -> None:
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None

    async def healthcheck(self) -> bool:
        if self._engine is None:
            return False

        try:
            async with self.engine.connect() as connection:
                await connection.execute(select(1))
        except Exception:
            return False

        return True
