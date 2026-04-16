# DevEx SRE Case — Deployment Insights

## The Scenario

You've joined the Developer Experience team at a company that runs hundreds of microservice deployments per week. The team has a **Deployment Registry API** — a service that tracks every deployment (who deployed what, where, when, and whether it succeeded).

Your task: build a **Deployment Insights API** that consumes the Registry and provides useful deployment metrics and analytics.

The Deployment Registry API source code is in the `deployment-registry/` directory. You'll need to get it running, then build your own service on top of it.

## Before You Start

**You are welcome and encouraged to use AI tools** (Copilot, ChatGPT, Claude, etc.) during this assignment. We use AI daily in our work and consider it a valuable skill. What matters is that you **understand what you've built** and can explain your decisions during the interview. We will ask you to walk through your code, discuss trade-offs, and explain why you made certain choices.

**Time expectation:** This assignment is designed to take approximately **4 hours**. There is a mandatory core path and optional extension tracks — focus on what you're strongest at. You do not need to complete everything.

**Language:** You may implement your Insights service in **C#**, **Python**, or **TypeScript** — your choice.

## Core Tasks (~2 hours)

These are mandatory. They provide the baseline we use to compare candidates.

### 1. Get the Deployment Registry running

- Read the source code in `deployment-registry/` to understand the API
- Set up MongoDB (Docker container, local install, or cloud free tier)
- Get the service running and seed it with data (see `deployment-registry/seed-data.json`)

### 2. Build the Deployment Insights service

Build a new microservice that calls the Deployment Registry API and exposes these endpoints:

| Method | Path | Description |
|--------|------|-------------|
| GET | `/insights/frequency` | Deployment frequency per service (daily/weekly) |
| GET | `/insights/lead-time` | Average time from deploy start to success, per service |
| GET | `/insights/failure-rate` | Failure and rollback rate per service and environment |
| GET | `/insights/latest` | Latest deployed version per service per environment |
| GET | `/health` | Health check (including: can it reach the Registry API?) |

Implement **at least 3 of the 5** endpoints. Your service should be stateless — all data comes from the Registry API.

### 3. Containerize

- Write Dockerfiles for both services
- Create a `docker-compose.yml` that runs everything (both services + MongoDB)
- Running `docker-compose up` should start a fully working system

### 4. CI Pipeline

Set up a GitHub Actions workflow that:

- Builds your Insights service
- Runs tests
- Builds a container image
- Pushes to GitHub Container Registry (ghcr.io)

> **Internally we use Google Artifact Registry**, but ghcr.io is free and doesn't require external accounts.

### 5. Tests

- Unit tests for your aggregation/calculation logic
- At least one integration test that verifies your service can talk to the Registry API

## Extension Tracks (~2 hours)

Pick one or more tracks based on what interests you. Going deep on one track is better than doing three tracks superficially.

### Track A: Infrastructure as Code

Write Terraform to provision the infrastructure needed to run the services.

| Option | Description |
|--------|-------------|
| **GCP** (if you have an account) | GKE Autopilot or Cloud Run, Artifact Registry, MongoDB Atlas free tier |
| **Dry-run GCP** | Write Terraform targeting GCP, validate with `terraform plan`, explain what `apply` would do |
| **Local K8s + Terraform** | Use the Terraform Kubernetes provider against kind/minikube |
| **Docker provider** | Use `kreuzwerker/docker` to manage containers via Terraform locally |

> **Internally we use GCP + Terraform with Atlantis** for plan/apply review workflows.

### Track B: Kubernetes & GitOps

- Write Kubernetes manifests (Deployments, Services, ConfigMaps) for both services + MongoDB
- Run on a local cluster (kind or minikube)
- **Bonus:** ArgoCD Application manifests for GitOps-style deployment

> **Internally we use GKE + ArgoCD** with an app-of-apps pattern.

### Track C: Observability & Monitoring

- Structured logging (JSON, with correlation IDs)
- Prometheus metrics: request latency histograms, error counters, dependency health gauge
- Grafana dashboard showing service health, request rates, error rates
- **Bonus:** alerting rules (high error rate, Registry API unreachable)

> **Internally we use Datadog** for metrics, logs, traces, and APM.

### Track D: Advanced CI/CD

- Multi-environment pipeline (staging → production with manual approval)
- Container image tagging strategy (commit SHA, semver, latest)
- Security scanning (Trivy or dependency audit)
- **Bonus:** automated rollback on health check failure

> **Internally we use GitHub Actions with reusable workflows**, Spinnaker for the monolith, and ArgoCD for microservices.

### Track E: Resilience & Testing

- Integration test suite using docker-compose (start deps, test, tear down)
- Contract tests between your service and the Registry API
- Fault injection: what happens when MongoDB dies? The Registry returns 500s? Slow responses?
- **Bonus:** retry with exponential backoff and circuit breaker

### Stretch Goal: Redis Caching

Combinable with any track:

- Add Redis as a cache layer in front of Registry API calls
- Cache invalidation (TTL or smarter)
- Cache hit/miss metrics
- Update docker-compose / IaC / K8s manifests accordingly

## What to Submit

1. **Fork** this repo to your public GitHub profile
2. Build your solution in the fork
3. Include a **README** in your solution explaining:
   - How to run everything (`docker-compose up` or equivalent)
   - Which endpoints you implemented and why
   - What decisions you made and trade-offs you considered
   - What you would improve given more time

## What Happens Next

During the interview (~90 minutes), you'll:

- **Screen share** and walk us through your code
- **Demo** the running system (start it up, show the endpoints working)
- **Discuss** your decisions — we're interested in _why_, not just _what_
- **Talk about** what you'd do differently in a production environment

We're evaluating problem-solving, technical depth, communication, and how you approach unfamiliar systems — not whether you completed every task perfectly.
