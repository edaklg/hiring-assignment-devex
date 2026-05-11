from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.client import check_registry_health

router = APIRouter()


@router.get("/health")
async def health():
    registry_ok = await check_registry_health()
    body = {
        "status": "healthy" if registry_ok else "degraded",
        "dependencies": {
            "registry": "reachable" if registry_ok else "unreachable",
        },
    }
    status_code = 200 if registry_ok else 503
    return JSONResponse(content=body, status_code=status_code)
