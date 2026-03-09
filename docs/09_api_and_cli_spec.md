# API and CLI Spec

## CLI
- `awb run`
- `awb compare`
- `awb eval`
- `awb optimize`
- `awb approve`
- `awb report`

## Service API (planned)
- `POST /runs`
- `GET /runs/{id}`
- `POST /runs/{id}/evaluate`
- `POST /runs/{id}/optimize`
- `GET /runs/{id}/traces`
- `GET /approvals/pending`
- `POST /approvals/{id}/decision`
- `GET /reports/{run_id}`
