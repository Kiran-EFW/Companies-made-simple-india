#!/usr/bin/env bash
#
# One-time GCP infrastructure setup for Companies Made Simple India.
#
# Prerequisites:
#   1. gcloud CLI installed and authenticated (gcloud auth login)
#   2. A GCP project with billing enabled
#
# Usage:
#   export GCP_PROJECT_ID=your-project-id
#   bash deploy/setup-gcp.sh
#
set -euo pipefail

# ── Configuration ───────────────────────────────────────
PROJECT_ID="${GCP_PROJECT_ID:?Set GCP_PROJECT_ID environment variable}"
REGION="${GCP_REGION:-asia-south1}"
DB_INSTANCE_NAME="${DB_INSTANCE_NAME:-cms-india-db}"
DB_TIER="${DB_TIER:-db-f1-micro}"          # Use db-custom-2-7680 for prod
DB_NAME="${DB_NAME:-cms_india}"
DB_USER="${DB_USER:-cms_india}"
REDIS_INSTANCE="${REDIS_INSTANCE:-cms-india-redis}"
REDIS_TIER="${REDIS_TIER:-BASIC}"
REDIS_SIZE="${REDIS_SIZE:-1}"              # GB
REPO_NAME="${REPO_NAME:-cms-india}"
VPC_CONNECTOR="${VPC_CONNECTOR:-cms-india-connector}"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  CMS India — GCP Infrastructure Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Project:  ${PROJECT_ID}"
echo "  Region:   ${REGION}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

gcloud config set project "${PROJECT_ID}"

# ── 1. Enable required APIs ────────────────────────────
echo "▶ Enabling GCP APIs..."
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  secretmanager.googleapis.com \
  vpcaccess.googleapis.com \
  compute.googleapis.com

echo "  ✓ APIs enabled"

# ── 2. Create Artifact Registry repository ─────────────
echo ""
echo "▶ Creating Artifact Registry repository..."
if gcloud artifacts repositories describe "${REPO_NAME}" \
     --location="${REGION}" --format="value(name)" 2>/dev/null; then
  echo "  ✓ Repository '${REPO_NAME}' already exists"
else
  gcloud artifacts repositories create "${REPO_NAME}" \
    --repository-format=docker \
    --location="${REGION}" \
    --description="CMS India container images"
  echo "  ✓ Repository '${REPO_NAME}' created"
fi

# ── 3. Create Cloud SQL (PostgreSQL) instance ──────────
echo ""
echo "▶ Creating Cloud SQL PostgreSQL instance..."
if gcloud sql instances describe "${DB_INSTANCE_NAME}" --format="value(name)" 2>/dev/null; then
  echo "  ✓ Instance '${DB_INSTANCE_NAME}' already exists"
else
  gcloud sql instances create "${DB_INSTANCE_NAME}" \
    --database-version=POSTGRES_15 \
    --tier="${DB_TIER}" \
    --region="${REGION}" \
    --storage-auto-increase \
    --backup-start-time=03:00 \
    --availability-type=zonal
  echo "  ✓ Instance '${DB_INSTANCE_NAME}' created"
fi

# Generate a random DB password
DB_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(24))")

# Set the DB user password
echo "  Setting database user password..."
gcloud sql users set-password "${DB_USER}" \
  --instance="${DB_INSTANCE_NAME}" \
  --password="${DB_PASSWORD}" 2>/dev/null || \
gcloud sql users create "${DB_USER}" \
  --instance="${DB_INSTANCE_NAME}" \
  --password="${DB_PASSWORD}"

# Create the database
echo "  Creating database..."
gcloud sql databases create "${DB_NAME}" \
  --instance="${DB_INSTANCE_NAME}" 2>/dev/null || echo "  (database already exists)"

CLOUD_SQL_CONNECTION="${PROJECT_ID}:${REGION}:${DB_INSTANCE_NAME}"
echo "  ✓ Cloud SQL connection: ${CLOUD_SQL_CONNECTION}"

# ── 4. Store secrets in Secret Manager ─────────────────
echo ""
echo "▶ Storing secrets in Secret Manager..."

# Database URL for Cloud SQL via Unix socket
DB_URL="postgresql://${DB_USER}:${DB_PASSWORD}@/${DB_NAME}?host=/cloudsql/${CLOUD_SQL_CONNECTION}"

# Store DB URL
echo -n "${DB_URL}" | gcloud secrets create cms-india-db-password \
  --data-file=- --replication-policy=automatic 2>/dev/null || \
echo -n "${DB_URL}" | gcloud secrets versions add cms-india-db-password --data-file=-
echo "  ✓ Secret 'cms-india-db-password' stored"

# Generate and store app secret key
APP_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo -n "${APP_SECRET}" | gcloud secrets create cms-india-secret-key \
  --data-file=- --replication-policy=automatic 2>/dev/null || \
echo -n "${APP_SECRET}" | gcloud secrets versions add cms-india-secret-key --data-file=-
echo "  ✓ Secret 'cms-india-secret-key' stored"

# ── 5. Create VPC Connector (for Memorystore access) ──
echo ""
echo "▶ Creating Serverless VPC Access connector..."
if gcloud compute networks vpc-access connectors describe "${VPC_CONNECTOR}" \
     --region="${REGION}" --format="value(name)" 2>/dev/null; then
  echo "  ✓ Connector '${VPC_CONNECTOR}' already exists"
else
  gcloud compute networks vpc-access connectors create "${VPC_CONNECTOR}" \
    --region="${REGION}" \
    --range=10.8.0.0/28 \
    --network=default
  echo "  ✓ VPC connector created"
fi

# ── 6. Create Memorystore Redis instance ───────────────
echo ""
echo "▶ Creating Memorystore Redis instance..."
if gcloud redis instances describe "${REDIS_INSTANCE}" \
     --region="${REGION}" --format="value(name)" 2>/dev/null; then
  echo "  ✓ Instance '${REDIS_INSTANCE}' already exists"
  REDIS_HOST=$(gcloud redis instances describe "${REDIS_INSTANCE}" \
    --region="${REGION}" --format="value(host)")
else
  gcloud redis instances create "${REDIS_INSTANCE}" \
    --region="${REGION}" \
    --tier="${REDIS_TIER}" \
    --size="${REDIS_SIZE}" \
    --redis-version=redis_7_0 \
    --network=default
  REDIS_HOST=$(gcloud redis instances describe "${REDIS_INSTANCE}" \
    --region="${REGION}" --format="value(host)")
  echo "  ✓ Redis instance created at ${REDIS_HOST}"
fi

# ── 7. Grant Cloud Build service account permissions ───
echo ""
echo "▶ Configuring IAM permissions..."
PROJECT_NUMBER=$(gcloud projects describe "${PROJECT_ID}" --format="value(projectNumber)")
CB_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

declare -a ROLES=(
  "roles/run.admin"
  "roles/iam.serviceAccountUser"
  "roles/secretmanager.secretAccessor"
  "roles/artifactregistry.writer"
)

for role in "${ROLES[@]}"; do
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${CB_SA}" \
    --role="${role}" \
    --condition=None \
    --quiet
done

# Also grant Cloud Run service account access to secrets
RUN_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${RUN_SA}" \
  --role="roles/secretmanager.secretAccessor" \
  --condition=None \
  --quiet
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${RUN_SA}" \
  --role="roles/cloudsql.client" \
  --condition=None \
  --quiet

echo "  ✓ IAM permissions configured"

# ── 8. Create Cloud Build trigger ──────────────────────
echo ""
echo "▶ Setup complete! Next steps:"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Cloud SQL connection:  ${CLOUD_SQL_CONNECTION}"
echo "  Redis host:            ${REDIS_HOST}"
echo "  VPC connector:         ${VPC_CONNECTOR}"
echo "  Artifact Registry:     ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}"
echo ""
echo "  To trigger a manual build:"
echo ""
echo "    gcloud builds submit \\"
echo "      --config=cloudbuild.yaml \\"
echo "      --substitutions=_CLOUD_SQL_CONNECTION=${CLOUD_SQL_CONNECTION},_REDIS_HOST=${REDIS_HOST} \\"
echo "      --region=${REGION}"
echo ""
echo "  To set up a GitHub trigger (auto-deploy on push to main):"
echo ""
echo "    gcloud builds triggers create github \\"
echo "      --repo-name=companies-made-simple-india \\"
echo "      --repo-owner=YOUR_GITHUB_ORG \\"
echo "      --branch-pattern='^main$' \\"
echo "      --build-config=cloudbuild.yaml \\"
echo "      --substitutions=_CLOUD_SQL_CONNECTION=${CLOUD_SQL_CONNECTION},_REDIS_HOST=${REDIS_HOST} \\"
echo "      --region=${REGION}"
echo ""
echo "  To add additional secrets (API keys, etc.):"
echo ""
echo "    echo -n 'your-key' | gcloud secrets create SECRET_NAME --data-file=-"
echo "    # Then add --update-secrets=ENV_VAR=SECRET_NAME:latest to the Cloud Run deploy step"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
