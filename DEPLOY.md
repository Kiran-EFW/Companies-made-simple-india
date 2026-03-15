# Deployment Guide — Companies Made Simple India

## Architecture

```
                    ┌─────────────────────────────────────────────┐
                    │              Google Cloud Platform           │
                    │           Project: sub-projects-483107       │
                    │           Region: asia-south1 (Mumbai)       │
                    │                                             │
  Users ──────────► │  ┌──────────────┐   ┌──────────────────┐   │
                    │  │   Frontend   │   │   Admin Portal   │   │
                    │  │  (Next.js)   │   │    (Next.js)     │   │
                    │  │  Port 3000   │   │    Port 3001     │   │
                    │  └──────┬───────┘   └────────┬─────────┘   │
                    │         │                    │              │
                    │         ▼                    ▼              │
                    │  ┌──────────────────────────────────┐      │
                    │  │        Backend API (FastAPI)      │      │
                    │  │           Port 8080               │      │
                    │  └──────┬───────────────┬───────────┘      │
                    │         │               │                  │
                    │    ┌────▼────┐    ┌─────▼──────┐          │
                    │    │ Cloud   │    │ Memorystore │          │
                    │    │  SQL    │    │   Redis 7   │          │
                    │    │ PG 18   │    │ 10.57.165.243│         │
                    │    └─────────┘    └─────────────┘          │
                    │         ▲               ▲                  │
                    │    ┌────┴────┐    ┌─────┴──────┐          │
                    │    │ Celery  │    │  Celery    │          │
                    │    │ Worker  │    │   Beat     │          │
                    │    └─────────┘    └────────────┘          │
                    └─────────────────────────────────────────────┘
```

## Cloud Run Services

| Service | URL | Port | CPU | Memory | Min/Max Instances |
|---------|-----|------|-----|--------|-------------------|
| Backend API | https://cms-india-backend-979970479540.asia-south1.run.app | 8080 | 2 | 1Gi | 1/10 |
| Celery Worker | Internal | 8080 | 2 | 1Gi | 1/5 |
| Celery Beat | Internal | 8080 | 1 | 512Mi | 1/1 |
| Frontend | https://cms-india-frontend-979970479540.asia-south1.run.app | 3000 | 1 | 512Mi | 0/10 |
| Admin Portal | https://cms-india-admin-979970479540.asia-south1.run.app | 3001 | 1 | 512Mi | 0/5 |

## Infrastructure

| Resource | Details |
|----------|---------|
| **GCP Project** | `sub-projects-483107` |
| **Region** | `asia-south1` (Mumbai) |
| **Artifact Registry** | `cms-india` (Docker) |
| **Cloud SQL** | Instance: `cms-india` (PostgreSQL, db-perf-optimized-N-8) |
| **Database** | `cms_india` / User: `cms_india` |
| **Memorystore Redis** | `cms-india-redis` (Redis 7.0, 1GB, IP: `10.57.165.243`) |
| **VPC Connector** | `cms-india-connector` (10.8.0.0/28, default network) |
| **Logs Bucket** | `gs://sub-projects-483107-cloudbuild-logs` |

## Secrets (Secret Manager)

| Secret Name | Contains |
|-------------|----------|
| `cms-india-db-password` | `DATABASE_URL` (PostgreSQL connection string with Cloud SQL Unix socket) |
| `cms-india-secret-key` | `SECRET_KEY` (application signing key) |

## Service Accounts

| Account | Purpose | Key Roles |
|---------|---------|-----------|
| `cloud-build-deployer@sub-projects-483107.iam.gserviceaccount.com` | Cloud Build triggers | Cloud Build Service Account, Cloud Run Admin, Service Account User, Secret Manager Secret Accessor, Artifact Registry Writer, Cloud SQL Client, Storage Admin, Logging Writer |
| `979970479540-compute@developer.gserviceaccount.com` | Cloud Run default SA | Secret Manager Secret Accessor, Cloud SQL Client |

## CI/CD — Cloud Build Triggers

Three separate triggers, each with path filters:

| Trigger | Config File | Path Filter | Deploys |
|---------|------------|-------------|---------|
| `deploy-cms-india-backend` | `backend/cloudbuild.yaml` | `backend/**` | Backend API, Celery Worker, Celery Beat |
| `deploy-cms-india-frontend` | `frontend/cloudbuild.yaml` | `frontend/**` | Frontend |
| `deploy-cms-india-admin` | `admin-portal/cloudbuild.yaml` | `admin-portal/**` | Admin Portal |

All triggers fire on push to `main` branch. Only the services affected by changed files are rebuilt.

## Environment Variables

### Backend (set in `backend/cloudbuild.yaml`)

| Variable | Value | Source |
|----------|-------|--------|
| `ENVIRONMENT` | `production` | cloudbuild.yaml |
| `DB_USER` | `cms_india` | cloudbuild.yaml |
| `DB_NAME` | `cms_india` | cloudbuild.yaml |
| `REDIS_URL` | `redis://10.57.165.243:6379/0` | cloudbuild.yaml |
| `CELERY_BROKER_URL` | `redis://10.57.165.243:6379/1` | cloudbuild.yaml |
| `CORS_ORIGINS` | Frontend + Admin Cloud Run URLs | cloudbuild.yaml |
| `FRONTEND_URL` | Frontend Cloud Run URL | cloudbuild.yaml |
| `DATABASE_URL` | PostgreSQL connection string | Secret Manager |
| `SECRET_KEY` | Application signing key | Secret Manager |

### Frontend & Admin Portal

| Variable | Value | Set At |
|----------|-------|--------|
| `NODE_ENV` | `production` | Runtime (cloudbuild.yaml) |
| `NEXT_PUBLIC_API_URL` | `/api/v1` | Build time (Dockerfile ARG) |

## Deploying Changes

### Automatic (recommended)

Push to `main` branch. Only affected services rebuild:

```bash
# Example: only backend changes
git add backend/
git commit -m "fix: update API endpoint"
git push origin main
# → Only deploy-cms-india-backend trigger fires
```

### Manual trigger

```bash
gcloud builds triggers run deploy-cms-india-backend --region=asia-south1 --branch=main
gcloud builds triggers run deploy-cms-india-frontend --region=asia-south1 --branch=main
gcloud builds triggers run deploy-cms-india-admin --region=asia-south1 --branch=main
```

### Monitor builds

```bash
# List recent builds
gcloud builds list --region=asia-south1 --limit=5

# Stream build logs
gcloud builds log BUILD_ID --region=asia-south1
```

## Celery on Cloud Run

Celery Worker and Beat run on Cloud Run using `start_celery.sh` which:
1. Starts a minimal HTTP health check server on `$PORT` (required by Cloud Run)
2. Exec's into the Celery process

Both services use `--no-cpu-throttling` so they run continuously.

## Adding API Keys

To add integration API keys (Razorpay, SendGrid, etc.), create secrets and update the backend deploy step:

```bash
# Create a new secret
echo -n "your-api-key" | gcloud secrets create SECRET_NAME --data-file=-

# Grant access to Cloud Run SA
gcloud secrets add-iam-policy-binding SECRET_NAME \
  --member="serviceAccount:979970479540-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

Then add to the `--update-secrets` flag in `backend/cloudbuild.yaml`:
```yaml
- --update-secrets=DATABASE_URL=cms-india-db-password:latest,SECRET_KEY=cms-india-secret-key:latest,RAZORPAY_KEY_ID=razorpay-key-id:latest
```

## Updating CORS Origins

If you add a custom domain, update CORS in `backend/cloudbuild.yaml` line 60:

```yaml
- --set-env-vars=^@^...@CORS_ORIGINS=https://yourdomain.com,https://admin.yourdomain.com@...
```

The `^@^` prefix tells gcloud to use `@` as the delimiter instead of `,` (since CORS values contain commas).

## Costs Estimate (Monthly)

| Resource | Config | Estimated Cost |
|----------|--------|---------------|
| Cloud SQL | db-perf-optimized-N-8 | Check GCP pricing |
| Memorystore Redis | 1GB Basic | ~$35 |
| Cloud Run (backend, min=1) | 2 vCPU, 1Gi | ~$50 |
| Cloud Run (celery-worker, min=1) | 2 vCPU, 1Gi | ~$50 |
| Cloud Run (celery-beat, min=1) | 1 vCPU, 512Mi | ~$25 |
| Cloud Run (frontend, min=0) | 1 vCPU, 512Mi | Pay-per-use |
| Cloud Run (admin, min=0) | 1 vCPU, 512Mi | Pay-per-use |
| Artifact Registry | Storage | ~$1 |
| VPC Connector | e2-micro instances | ~$7 |
