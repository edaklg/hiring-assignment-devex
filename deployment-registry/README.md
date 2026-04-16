# Deployment Registry API

A REST API for storing and retrieving deployment records. Built with C# / .NET 10 and MongoDB.

## What it does

This service tracks deployments across multiple services and environments. Each deployment record captures who deployed what, where, and when — along with its current status.

## Requirements

- .NET 10 SDK
- MongoDB

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/deployments` | List deployments |
| GET | `/api/deployments/{id}` | Get a single deployment |
| POST | `/api/deployments` | Create a deployment record |
| PUT | `/api/deployments/{id}` | Update a deployment record |
| GET | `/api/health` | Health check |

### Filtering

The `GET /api/deployments` endpoint supports query parameters:

- `serviceName` — filter by service name (exact match)
- `environment` — filter by environment (`staging` or `production`)
- `status` — filter by deployment status

### Deployment statuses

`Queued` → `Building` → `Deploying` → `Succeeded` | `Failed` | `RolledBack`

## Seed Data

A `seed-data.json` file is provided with sample deployment records. You can import it into MongoDB using:

```bash
mongoimport --db deployment-registry --collection deployments --jsonArray --file seed-data.json
```

Or use the `POST /api/deployments` endpoint to create records programmatically.
