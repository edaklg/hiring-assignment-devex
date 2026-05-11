from app.aggregations import (
    compute_frequency,
    compute_lead_time,
    compute_failure_rate,
    compute_latest,
)


DEPLOYMENTS = [
    {
        "serviceName": "auth-proxy",
        "environment": "staging",
        "version": "1.0.0",
        "status": "Succeeded",
        "deployedBy": "alice",
        "startedAt": "2026-01-01T10:00:00Z",
        "finishedAt": "2026-01-01T10:20:00Z",  # 1200s
    },
    {
        "serviceName": "auth-proxy",
        "environment": "staging",
        "version": "1.0.1",
        "status": "Failed",
        "deployedBy": "alice",
        "startedAt": "2026-01-02T10:00:00Z",
        "finishedAt": "2026-01-02T10:10:00Z",
    },
    {
        "serviceName": "auth-proxy",
        "environment": "production",
        "version": "1.0.0",
        "status": "Succeeded",
        "deployedBy": "bob",
        "startedAt": "2026-01-03T08:00:00Z",
        "finishedAt": "2026-01-03T08:30:00Z",  # 1800s
    },
    {
        "serviceName": "billing-api",
        "environment": "staging",
        "version": "2.0.0",
        "status": "RolledBack",
        "deployedBy": "carol",
        "startedAt": "2026-01-01T12:00:00Z",
        "finishedAt": "2026-01-01T12:15:00Z",
    },
    {
        "serviceName": "billing-api",
        "environment": "staging",
        "version": "2.0.1",
        "status": "Succeeded",
        "deployedBy": "carol",
        "startedAt": "2026-01-01T14:00:00Z",
        "finishedAt": "2026-01-01T14:10:00Z",  # 600s
    },
    # In-progress deployment — should be excluded from lead-time and failure-rate
    {
        "serviceName": "auth-proxy",
        "environment": "staging",
        "version": "1.0.2",
        "status": "Deploying",
        "deployedBy": "alice",
        "startedAt": "2026-01-04T09:00:00Z",
        "finishedAt": None,
    },
]


class TestComputeFrequency:
    def test_daily_counts(self):
        result = compute_frequency(DEPLOYMENTS, granularity="daily")
        by_service = {r["service"]: r["deployments"] for r in result}

        # auth-proxy: Jan 1, Jan 2, Jan 3, Jan 4 → 1 each
        assert len(by_service["auth-proxy"]) == 4
        assert all(d["count"] == 1 for d in by_service["auth-proxy"])

        # billing-api: Jan 1 → 2 deployments
        assert by_service["billing-api"] == [{"period": "2026-01-01", "count": 2}]

    def test_weekly_counts(self):
        result = compute_frequency(DEPLOYMENTS, granularity="weekly")
        by_service = {r["service"]: r["deployments"] for r in result}

        # All auth-proxy deployments fall in the same ISO week
        assert len(by_service["auth-proxy"]) == 1
        assert by_service["auth-proxy"][0]["count"] == 4

    def test_returns_all_services(self):
        result = compute_frequency(DEPLOYMENTS)
        services = {r["service"] for r in result}
        assert services == {"auth-proxy", "billing-api"}


class TestComputeLeadTime:
    def test_averages_succeeded_only(self):
        result = compute_lead_time(DEPLOYMENTS)
        by_service = {r["service"]: r for r in result}

        # auth-proxy: (1200 + 1800) / 2 = 1500s
        assert by_service["auth-proxy"]["avg_lead_time_seconds"] == 1500.0
        assert by_service["auth-proxy"]["sample_size"] == 2

        # billing-api: only 1 Succeeded (600s)
        assert by_service["billing-api"]["avg_lead_time_seconds"] == 600.0
        assert by_service["billing-api"]["sample_size"] == 1

    def test_excludes_non_terminal_statuses(self):
        result = compute_lead_time(DEPLOYMENTS)
        by_service = {r["service"]: r for r in result}
        # sample_size for auth-proxy should be 2, not 3 (excludes Deploying)
        assert by_service["auth-proxy"]["sample_size"] == 2

    def test_empty_input(self):
        assert compute_lead_time([]) == []


class TestComputeFailureRate:
    def test_rate_calculation(self):
        result = compute_failure_rate(DEPLOYMENTS)
        by_key = {(r["service"], r["environment"]): r for r in result}

        # auth-proxy/staging: 1 Failed out of 2 terminal = 0.5
        assert by_key[("auth-proxy", "staging")]["failure_rate"] == 0.5
        assert by_key[("auth-proxy", "staging")]["total_deployments"] == 2

        # auth-proxy/production: 0 failures out of 1 = 0.0
        assert by_key[("auth-proxy", "production")]["failure_rate"] == 0.0

        # billing-api/staging: 1 RolledBack out of 2 = 0.5
        assert by_key[("billing-api", "staging")]["failure_rate"] == 0.5

    def test_excludes_in_progress(self):
        result = compute_failure_rate(DEPLOYMENTS)
        by_key = {(r["service"], r["environment"]): r for r in result}
        # auth-proxy/staging has a Deploying record that must not be counted
        assert by_key[("auth-proxy", "staging")]["total_deployments"] == 2

    def test_empty_input(self):
        assert compute_failure_rate([]) == []


class TestComputeLatest:
    def test_picks_most_recent_per_service_env(self):
        result = compute_latest(DEPLOYMENTS)
        by_key = {(r["service"], r["environment"]): r for r in result}

        # auth-proxy/staging: latest is 1.0.2 (Jan 4)
        assert by_key[("auth-proxy", "staging")]["version"] == "1.0.2"

        # auth-proxy/production: only one deployment
        assert by_key[("auth-proxy", "production")]["version"] == "1.0.0"

        # billing-api/staging: latest is 2.0.1 (14:00 vs 12:00)
        assert by_key[("billing-api", "staging")]["version"] == "2.0.1"

    def test_returns_correct_fields(self):
        result = compute_latest(DEPLOYMENTS)
        for entry in result:
            assert {"service", "environment", "version", "status", "deployed_by", "started_at"}.issubset(entry)

    def test_empty_input(self):
        assert compute_latest([]) == []
