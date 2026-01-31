from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from app.logger import logger
from app.routers import router
from app.routers.infra import infra_router
from app.storage.db.base import db_manager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    db_manager.connect()
    logger.info("App initialized")
    yield
    await db_manager.close()


app = FastAPI(lifespan=lifespan, docs_url="/docs", openapi_url="/openapi/openapi.json")
app.include_router(router, prefix="/api")
app.include_router(infra_router, prefix="/api/infra")
