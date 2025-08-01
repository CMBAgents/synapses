#!/bin/bash

# GCP Deployment Script for CMB Agent Info

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=""
REGION="us-central1"
SERVICE_NAME="cmbagent-info"
CONTEXTS_BUCKET=""
STATIC_BUCKET=""

echo -e "${BLUE}🚀 GCP Deployment Script for CMB Agent Info${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

if ! command_exists gcloud; then
    echo -e "${RED}❌ Google Cloud CLI is not installed${NC}"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

if ! command_exists node; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    exit 1
fi

if ! command_exists npm; then
    echo -e "${RED}❌ npm is not installed${NC}"
    exit 1
fi

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites are installed${NC}"

# Get project ID
if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}🔍 Getting current project...${NC}"
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "")
    
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${YELLOW}Please enter your GCP Project ID:${NC}"
        read -r PROJECT_ID
    else
        echo -e "${GREEN}Using project: $PROJECT_ID${NC}"
    fi
fi

# Set project
gcloud config set project "$PROJECT_ID"

# Set bucket names
CONTEXTS_BUCKET="${PROJECT_ID}-contexts"
STATIC_BUCKET="${PROJECT_ID}-static"

echo -e "${BLUE}📦 Project: $PROJECT_ID${NC}"
echo -e "${BLUE}📦 Contexts Bucket: $CONTEXTS_BUCKET${NC}"
echo -e "${BLUE}📦 Static Bucket: $STATIC_BUCKET${NC}"

# Enable required APIs
echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com

echo -e "${GREEN}✅ APIs enabled${NC}"

# Create buckets
echo -e "${YELLOW}🗂️ Creating storage buckets...${NC}"

# Create contexts bucket
if ! gsutil ls -b "gs://$CONTEXTS_BUCKET" >/dev/null 2>&1; then
    gsutil mb "gs://$CONTEXTS_BUCKET"
    echo -e "${GREEN}✅ Created contexts bucket: $CONTEXTS_BUCKET${NC}"
else
    echo -e "${GREEN}✅ Contexts bucket already exists: $CONTEXTS_BUCKET${NC}"
fi

# Create static bucket
if ! gsutil ls -b "gs://$STATIC_BUCKET" >/dev/null 2>&1; then
    gsutil mb "gs://$STATIC_BUCKET"
    gsutil iam ch allUsers:objectViewer "gs://$STATIC_BUCKET"
    echo -e "${GREEN}✅ Created static bucket: $STATIC_BUCKET${NC}"
else
    echo -e "${GREEN}✅ Static bucket already exists: $STATIC_BUCKET${NC}"
fi

# Configure CORS
echo -e "${YELLOW}🔧 Configuring CORS...${NC}"

cat > /tmp/cors.json << EOF
[
  {
    "origin": ["*"],
    "method": ["GET", "HEAD", "PUT", "POST", "DELETE"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]
EOF

gsutil cors set /tmp/cors.json "gs://$CONTEXTS_BUCKET"
gsutil cors set /tmp/cors.json "gs://$STATIC_BUCKET"

echo -e "${GREEN}✅ CORS configured${NC}"

# Create service account
echo -e "${YELLOW}🔐 Creating service account...${NC}"

SERVICE_ACCOUNT_NAME="context-updater"
SERVICE_ACCOUNT_EMAIL="$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"

if ! gcloud iam service-accounts describe "$SERVICE_ACCOUNT_EMAIL" >/dev/null 2>&1; then
    gcloud iam service-accounts create "$SERVICE_ACCOUNT_NAME" \
        --display-name="Context Updater Service Account"
    echo -e "${GREEN}✅ Created service account: $SERVICE_ACCOUNT_EMAIL${NC}"
else
    echo -e "${GREEN}✅ Service account already exists: $SERVICE_ACCOUNT_EMAIL${NC}"
fi

# Grant permissions
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/run.invoker"

echo -e "${GREEN}✅ Permissions granted${NC}"

# Download credentials
echo -e "${YELLOW}🔑 Downloading credentials...${NC}"

if [ ! -f "gcp-credentials.json" ]; then
    gcloud iam service-accounts keys create gcp-credentials.json \
        --iam-account="$SERVICE_ACCOUNT_EMAIL"
    echo -e "${GREEN}✅ Credentials downloaded${NC}"
else
    echo -e "${GREEN}✅ Credentials already exist${NC}"
fi

# Create environment file
echo -e "${YELLOW}⚙️ Creating environment configuration...${NC}"

cat > .env.local << EOF
# GCP Configuration
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
GOOGLE_CLOUD_BUCKET=$CONTEXTS_BUCKET
GOOGLE_CLOUD_STATIC_BUCKET=$STATIC_BUCKET
GOOGLE_APPLICATION_CREDENTIALS=./gcp-credentials.json

# Next.js Configuration
NEXT_PUBLIC_GCP_BUCKET=$CONTEXTS_BUCKET
NEXT_PUBLIC_GCP_STATIC_BUCKET=$STATIC_BUCKET
EOF

echo -e "${GREEN}✅ Environment file created${NC}"

# Install dependencies
echo -e "${YELLOW}📦 Installing dependencies...${NC}"
npm install
python3 scripts/install-dependencies.py

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Build application
echo -e "${YELLOW}🔨 Building application...${NC}"
npm run build

echo -e "${GREEN}✅ Application built${NC}"

# Deploy to Cloud Run
echo -e "${YELLOW}🚀 Deploying to Cloud Run...${NC}"

gcloud run deploy "$SERVICE_NAME" \
    --source . \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --set-env-vars "GOOGLE_CLOUD_BUCKET=$CONTEXTS_BUCKET" \
    --set-env-vars "GOOGLE_CLOUD_STATIC_BUCKET=$STATIC_BUCKET" \
    --set-env-vars "GOOGLE_APPLICATION_CREDENTIALS=/app/gcp-credentials.json" \
    --service-account="$SERVICE_ACCOUNT_EMAIL" \
    --memory=2Gi \
    --cpu=2 \
    --max-instances=10 \
    --min-instances=0

echo -e "${GREEN}✅ Application deployed${NC}"

# Get service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)")

echo -e "${GREEN}🎉 Deployment complete!${NC}"
echo -e "${BLUE}🌐 Service URL: $SERVICE_URL${NC}"

# Test health endpoint
echo -e "${YELLOW}🏥 Testing health endpoint...${NC}"
sleep 10

if curl -f "$SERVICE_URL/api/health" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${YELLOW}⚠️ Health check failed (service might still be starting)${NC}"
fi

# Setup automated context updates
echo -e "${YELLOW}🔄 Setting up automated context updates...${NC}"

# Create Cloud Function for context updates
cat > /tmp/function-main.py << 'EOF'
import functions_framework
import subprocess
import os
import sys

@functions_framework.http
def update_contexts(request):
    """HTTP Cloud Function to update contexts."""
    
    # Set environment variables
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/tmp/credentials.json'
    os.environ['GOOGLE_CLOUD_PROJECT'] = os.environ.get('GOOGLE_CLOUD_PROJECT', '')
    os.environ['GOOGLE_CLOUD_BUCKET'] = os.environ.get('GOOGLE_CLOUD_BUCKET', '')
    
    try:
        # Run the context updater
        result = subprocess.run([
            'python', '/workspace/scripts/auto-update-contexts.py', 'once'
        ], capture_output=True, text=True, timeout=540)  # 9 minutes timeout
        
        return {
            'status': 'success' if result.returncode == 0 else 'error',
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except subprocess.TimeoutExpired:
        return {
            'status': 'timeout',
            'error': 'Function timed out after 9 minutes'
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }
EOF

# Deploy Cloud Function
echo -e "${YELLOW}📦 Deploying Cloud Function...${NC}"

gcloud functions deploy context-updater \
    --runtime python39 \
    --trigger-http \
    --allow-unauthenticated \
    --region "$REGION" \
    --source /tmp \
    --entry-point update_contexts \
    --timeout 540s \
    --memory 2Gi \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --set-env-vars "GOOGLE_CLOUD_BUCKET=$CONTEXTS_BUCKET"

# Get function URL
FUNCTION_URL=$(gcloud functions describe context-updater --region="$REGION" --format="value(httpsTrigger.url)")

# Create Cloud Scheduler job
echo -e "${YELLOW}⏰ Setting up Cloud Scheduler...${NC}"

gcloud scheduler jobs create http context-update-job \
    --schedule="0 * * * *" \
    --uri="$FUNCTION_URL" \
    --http-method=POST \
    --location="$REGION" \
    --description="Hourly context update job"

echo -e "${GREEN}✅ Automated updates configured${NC}"

# Clean up
rm -f /tmp/cors.json /tmp/function-main.py

# Final summary
echo -e "${BLUE}"
echo "=========================================="
echo "🎉 DEPLOYMENT COMPLETE!"
echo "=========================================="
echo "Project ID: $PROJECT_ID"
echo "Service URL: $SERVICE_URL"
echo "Contexts Bucket: gs://$CONTEXTS_BUCKET"
echo "Static Bucket: gs://$STATIC_BUCKET"
echo "Region: $REGION"
echo ""
echo "📋 Useful Commands:"
echo "  View logs: gcloud logs tail --project=$PROJECT_ID"
echo "  Check service: gcloud run services describe $SERVICE_NAME --region=$REGION"
echo "  Update contexts: python scripts/auto-update-contexts.py once"
echo "  Monitor: python scripts/monitor-updater.py status"
echo ""
echo "🔗 Links:"
echo "  Cloud Console: https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME"
echo "  Storage Console: https://console.cloud.google.com/storage/browser"
echo "=========================================="
echo -e "${NC}" 