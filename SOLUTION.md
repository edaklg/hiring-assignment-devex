# Deployment Insights — Solution

## Running the system

```bash
docker compose up --build
```

That starts MongoDB, seeds it with the provided data, boots the Deployment Registry, and starts the Insights API. No other setup needed.

| Service | URL |
|---|---|
| Deployment Insights API | http://localhost:8000 |
| Deployment Registry API | http://localhost:8080 |

To stop and clean up:

```bash
docker compose down -v
```

## Endpoints implemented

All five endpoints are implemented.

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check — reports whether the Registry API is reachable |
| GET | `/insights/frequency` | Deployment count per service, grouped by day or week (`?granularity=weekly`) |
| GET | `/insights/lead-time` | Average time from deploy start to success, per service |
| GET | `/insights/failure-rate` | Failed + RolledBack rate per service and environment |
| GET | `/insights/latest` | Most recent deployment per service per environment |

### Example responses

```bash
# Deployment frequency (daily by default, or ?granularity=weekly)
curl http://localhost:8000/insights/frequency

# Lead time per service (Succeeded deployments only)
curl http://localhost:8000/insights/lead-time

# Failure rate per service and environment
curl http://localhost:8000/insights/failure-rate

# Latest deployment per service per environment
curl http://localhost:8000/insights/latest
```

## Architecture

```
[Client]
   │
   ▼
[Insights API]  (Python / FastAPI, port 8000)
   │  stateless — all data fetched live from Registry
   ▼
[Deployment Registry API]  (C# / .NET 10, port 8080)
   │
   ▼
[MongoDB]  (port 27017, seeded on first boot)
```

The Insights service is intentionally stateless. It holds no local state and fetches everything from the Registry on each request. This makes it trivially scalable and keeps the operational surface small — no cache to invalidate, no secondary database to manage.

## Key decisions and trade-offs

**Stateless Insights service**
The service makes live calls to the Registry on every request rather than maintaining its own read model. This is simple and always consistent, but it means every insights request costs a full Registry fetch. At scale, a read-through cache (Redis, short TTL) or a pre-aggregated materialized view would be the right next step.

**Aggregations in Python, not MongoDB**
Aggregation logic lives in `insights/app/aggregations.py` as pure functions over plain Python lists. This makes them fast to test (no database needed), easy to reason about, and straightforward to change. The trade-off is that the Registry API fetches the full collection on each request. For large datasets, pushing aggregation into MongoDB pipelines would reduce data transfer significantly.

**In-progress deployments excluded from metrics**
`failure-rate` and `lead-time` only count terminal statuses (`Succeeded`, `Failed`, `RolledBack`). Including in-progress deployments in failure rate would skew the numbers; including them in lead time would be meaningless. The `latest` endpoint intentionally includes all statuses so operators can see a deployment currently in flight.

**Cloud Run over GKE for production (Track A)**
The Terraform provisions Cloud Run services rather than Kubernetes. Cloud Run scales to zero, has no cluster overhead, and is a natural fit for these two stateless HTTP services. GKE would be the right choice if the team needed more control over networking, needed to co-locate services, or had workloads that don't fit the HTTP request model.

**Registry kept private in production**
In the Terraform config, only the Insights service is exposed publicly. The Registry has no authentication layer, so it's kept internal — accessible only to the Insights service account via IAM. In production you'd want to add authentication to the Registry itself regardless.

**MongoDB connection string in Secret Manager**
The connection string is stored in GCP Secret Manager and mounted into Cloud Run at runtime. It never appears in environment variable definitions in plaintext or in source control.

## CI pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push:

1. **Boots the full stack** with `docker compose up --build`
2. **Waits for services to be healthy**, then runs unit tests and integration tests
3. On success, **builds and pushes the Insights image** to GitHub Container Registry (`ghcr.io`) tagged with the commit SHA and branch name

The Registry service image is built as part of the compose stack in CI but not independently pushed — it's provided code, not owned by this repo.

## What I'd improve given more time

- **Caching** — a Redis layer in front of Registry calls with a short TTL (30–60s) would make the endpoints fast under load without meaningful staleness
- **Registry authentication** — the Registry API has no auth; in production it should require a token or be network-isolated
- **Pagination** — `GET /api/deployments` returns all records unbounded; at scale this needs cursor-based pagination on the Registry side and the Insights aggregations would need to handle paginated fetches
- **Structured logging and tracing** — JSON logs with a request correlation ID passed through to Registry calls, so a single slow insights request can be traced end-to-end
- **Alerting rules** — Prometheus metrics + Grafana alerts on high failure rate or Registry unreachability would complete the observability picture
- **Terraform remote state** — the current config has no backend configured; in a team setting this would use GCS for state with locking

## Terraform (Track A — dry run)

The `terraform/` directory provisions the production infrastructure on GCP:

- **Artifact Registry** — Docker image repository
- **Secret Manager** — MongoDB Atlas connection string
- **Cloud Run** — one service each for Registry and Insights
- **IAM** — least-privilege service accounts; Insights can invoke Registry, Registry can read the secret, only Insights is public

To validate (no GCP credentials needed):

```bash
cd terraform
terraform init
terraform validate
```

To plan against a real project:

```bash
terraform plan \
  -var="project_id=YOUR_PROJECT_ID" \
  -var="mongo_connection_string=YOUR_ATLAS_URI"
```
