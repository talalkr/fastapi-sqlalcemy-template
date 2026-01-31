from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.routers.deps import InfraServiceDep

from fastapi import APIRouter, Response

infra_router = APIRouter(tags=["infra"])


@infra_router.get("/healthcheck", response_model=bool)
async def healthcheck(response: Response, infra_service: InfraServiceDep) -> bool:
    return await infra_service.healthcheck()
