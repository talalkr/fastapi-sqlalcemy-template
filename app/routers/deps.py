from typing import Annotated
from fastapi import Depends

from app.services.infra_service import InfraService


async def get_infra_service() -> InfraService:
    return InfraService()


InfraServiceDep = Annotated[InfraService, Depends(get_infra_service)]
