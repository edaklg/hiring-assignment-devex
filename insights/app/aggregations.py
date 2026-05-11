from collections import defaultdict
from datetime import datetime, timezone


def _parse_dt(value: str) -> datetime:
    # Registry returns ISO 8601 with trailing Z
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def compute_frequency(deployments: list[dict], granularity: str = "daily") -> list[dict]:
    """Count deployments per service grouped by day or week."""
    buckets: dict[tuple, int] = defaultdict(int)

    for d in deployments:
        started = _parse_dt(d["startedAt"])
        service = d["serviceName"]

        if granularity == "weekly":
            # ISO week key: e.g. "2024-W03"
            key = f"{started.isocalendar().year}-W{started.isocalendar().week:02d}"
        else:
            key = started.date().isoformat()

        buckets[(service, key)] += 1

    result: dict[str, list] = defaultdict(list)
    for (service, period), count in sorted(buckets.items()):
        result[service].append({"period": period, "count": count})

    return [{"service": svc, "deployments": periods} for svc, periods in sorted(result.items())]


def compute_lead_time(deployments: list[dict]) -> list[dict]:
    """Average seconds from startedAt to finishedAt for Succeeded deployments, per service."""
    durations: dict[str, list[float]] = defaultdict(list)

    for d in deployments:
        if d.get("status") != "Succeeded" or not d.get("finishedAt"):
            continue
        started = _parse_dt(d["startedAt"])
        finished = _parse_dt(d["finishedAt"])
        durations[d["serviceName"]].append((finished - started).total_seconds())

    return [
        {
            "service": svc,
            "avg_lead_time_seconds": round(sum(vals) / len(vals), 1),
            "sample_size": len(vals),
        }
        for svc, vals in sorted(durations.items())
    ]


def compute_failure_rate(deployments: list[dict]) -> list[dict]:
    """Failure+rollback rate per service and environment."""
    total: dict[tuple, int] = defaultdict(int)
    failed: dict[tuple, int] = defaultdict(int)

    terminal = {"Succeeded", "Failed", "RolledBack"}

    for d in deployments:
        if d.get("status") not in terminal:
            continue
        key = (d["serviceName"], d["environment"])
        total[key] += 1
        if d["status"] in {"Failed", "RolledBack"}:
            failed[key] += 1

    return [
        {
            "service": svc,
            "environment": env,
            "total_deployments": total[(svc, env)],
            "failed_deployments": failed[(svc, env)],
            "failure_rate": round(failed[(svc, env)] / total[(svc, env)], 4),
        }
        for (svc, env) in sorted(total.keys())
    ]


def compute_latest(deployments: list[dict]) -> list[dict]:
    """Most recent deployment per service per environment."""
    latest: dict[tuple, dict] = {}

    for d in deployments:
        key = (d["serviceName"], d["environment"])
        if key not in latest or _parse_dt(d["startedAt"]) > _parse_dt(latest[key]["startedAt"]):
            latest[key] = d

    return [
        {
            "service": svc,
            "environment": env,
            "version": d["version"],
            "status": d["status"],
            "deployed_by": d["deployedBy"],
            "started_at": d["startedAt"],
        }
        for (svc, env), d in sorted(latest.items())
    ]
