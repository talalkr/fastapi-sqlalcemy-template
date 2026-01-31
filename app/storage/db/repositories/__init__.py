from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.storage.db.repositories.base_async_repository import BaseAsyncRepository

all_repositories: list[type[BaseAsyncRepository]] = []  # type: ignore[type-arg]
