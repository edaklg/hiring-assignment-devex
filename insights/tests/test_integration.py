"""
Integration test: verifies the Insights service can talk to the Registry API.
Requires REGISTRY_URL to point at a running Registry instance.
Skipped automatically if the Registry is unreachable.
"""
import os
import pytest
import httpx

REGISTRY_URL = os.environ.get("REGISTRY_URL", "http://localhost:8080")
INSIGHTS_URL = os.environ.get("INSIGHTS_URL", "http://localhost:8000")


def registry_is_up() -> bool:
    try:
        return httpx.get(f"{REGISTRY_URL}/api/health", timeout=3).status_code == 200
    except Exception:
        return False


def insights_is_up() -> bool:
    try:
        return httpx.get(f"{INSIGHTS_URL}/health", timeout=3).status_code == 200
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not (registry_is_up() and insights_is_up()),
    reason="Registry or Insights service not reachable",
)


def test_health_reports_registry_reachable():
    response = httpx.get(f"{INSIGHTS_URL}/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["dependencies"]["registry"] == "reachable"


@pytest.mark.parametrize("endpoint", [
    "/insights/frequency",
    "/insights/lead-time",
    "/insights/failure-rate",
    "/insights/latest",
])
def test_insights_endpoint_returns_list(endpoint):
    response = httpx.get(f"{INSIGHTS_URL}{endpoint}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_frequency_weekly_granularity():
    response = httpx.get(f"{INSIGHTS_URL}/insights/frequency?granularity=weekly")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    for entry in data:
        assert "service" in entry
        for bucket in entry["deployments"]:
            assert "W" in bucket["period"]  # ISO week format e.g. "2026-W03"
