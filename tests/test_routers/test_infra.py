from httpx import AsyncClient  # noqa TC002


class TestInfra:
    async def test_healthcheck(self, client: AsyncClient) -> None:
        response = await client.get("/api/infra/healthcheck")
        assert response.status_code == 200
        assert response.text == "true"
