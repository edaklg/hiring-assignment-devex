import os
import httpx

REGISTRY_URL = os.environ.get("REGISTRY_URL", "http://localhost:8080")


async def fetch_deployments(
    service_name: str | None = None,
    environment: str | None = None,
    status: str | None = None,
) -> list[dict]:
    params = {}
    if service_name:
        params["serviceName"] = service_name
    if environment:
        params["environment"] = environment
    if status:
        params["status"] = status

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(f"{REGISTRY_URL}/api/deployments", params=params)
        response.raise_for_status()
        return response.json()


async def check_registry_health() -> bool:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{REGISTRY_URL}/api/health")
            return response.status_code == 200
    except Exception:
        return False
