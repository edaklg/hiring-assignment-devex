from typing import Literal
from fastapi import APIRouter, HTTPException, Query
from app.client import fetch_deployments
from app import aggregations

router = APIRouter(prefix="/insights")


@router.get("/frequency")
async def frequency(granularity: Literal["daily", "weekly"] = Query("daily")):
    deployments = await fetch_deployments()
    return aggregations.compute_frequency(deployments, granularity)


@router.get("/lead-time")
async def lead_time():
    deployments = await fetch_deployments()
    return aggregations.compute_lead_time(deployments)


@router.get("/failure-rate")
async def failure_rate():
    deployments = await fetch_deployments()
    return aggregations.compute_failure_rate(deployments)


@router.get("/latest")
async def latest():
    deployments = await fetch_deployments()
    return aggregations.compute_latest(deployments)
