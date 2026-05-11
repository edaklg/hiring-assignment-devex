from fastapi import FastAPI
from app.routers import health, insights

app = FastAPI(title="Deployment Insights API")

app.include_router(health.router)
app.include_router(insights.router)
