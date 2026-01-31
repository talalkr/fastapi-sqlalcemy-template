import asyncio
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

    from fastapi import FastAPI

    from app.storage.db.connection_manager import ConnectionManager

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.storage.db.base import db_manager as app_db_manager
from app.storage.db.repositories import all_repositories


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop]:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def app_session(event_loop: asyncio.AbstractEventLoop) -> FastAPI:
    return app


@pytest.fixture
async def client(app_session: FastAPI) -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(
        transport=ASGITransport(app_session), base_url="http://test"
    ) as test_client:
        yield test_client


@pytest.fixture(scope="session", autouse=True)
async def db_manager() -> AsyncGenerator[ConnectionManager]:
    app_db_manager.connect()
    yield app_db_manager
    await app_db_manager.close()


@pytest.fixture(autouse=True)
async def isolation() -> AsyncGenerator[bool]:
    for repository in all_repositories:
        await repository().delete_all()
    yield True
