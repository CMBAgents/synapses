# 🚀 GCP Deployment Guide

This guide will help you deploy your site on Google Cloud Platform with Cloud Storage bucket for data.

## 📋 Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud CLI** installed
3. **Node.js** and **npm** installed
4. **Python** 3.8+ installed

## 🔧 Initial Setup

### 1. Install Google Cloud CLI

```bash
# macOS
brew install google-cloud-sdk

# Or download from: https://cloud.google.com/sdk/docs/install
```

### 2. Initialize and authenticate

```bash
# Initialize gcloud
gcloud init

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable compute.googleapis.com
```

## 🗂️ Cloud Storage Bucket Setup

### 1. Create Storage Bucket

```bash
# Create bucket for contexts
gsutil mb gs://YOUR_PROJECT_ID-contexts

# Create bucket for static assets
gsutil mb gs://YOUR_PROJECT_ID-static

# Make buckets public (for static hosting)
gsutil iam ch allUsers:objectViewer gs://YOUR_PROJECT_ID-static
```

### 2. Configure CORS for bucket

Create `cors.json`:

```json
[
  {
    "origin": ["*"],
    "method": ["GET", "HEAD", "PUT", "POST", "DELETE"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]
```

Apply CORS:

```bash
gsutil cors set cors.json gs://YOUR_PROJECT_ID-contexts
gsutil cors set cors.json gs://YOUR_PROJECT_ID-static
```

## ⚙️ Configuration Files

### 1. Update cloud-config.json

```json
{
  "provider": "gcp",
  "bucket_name": "YOUR_PROJECT_ID-contexts",
  "region": "us-central1",
  "project_id": "YOUR_PROJECT_ID",
  "static_bucket": "YOUR_PROJECT_ID-static",
  "sync_enabled": true,
  "backup_enabled": true,
  "credentials_file": "gcp-credentials.json"
}
```

### 2. Create GCP credentials

```bash
# Create service account
gcloud iam service-accounts create context-updater \
  --display-name="Context Updater Service Account"

# Grant storage permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:context-updater@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

# Download credentials
gcloud iam service-accounts keys create gcp-credentials.json \
  --iam-account=context-updater@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

### 3. Environment variables

Create `.env.local`:

```bash
# GCP Configuration
GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
GOOGLE_CLOUD_BUCKET=YOUR_PROJECT_ID-contexts
GOOGLE_CLOUD_STATIC_BUCKET=YOUR_PROJECT_ID-static
GOOGLE_APPLICATION_CREDENTIALS=./gcp-credentials.json

# Next.js Configuration
NEXT_PUBLIC_GCP_BUCKET=YOUR_PROJECT_ID-contexts
NEXT_PUBLIC_GCP_STATIC_BUCKET=YOUR_PROJECT_ID-static
```

## 🏗️ Application Configuration

### 1. Update Next.js configuration

```javascript
// next.config.mjs
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  env: {
    GCP_BUCKET: process.env.GOOGLE_CLOUD_BUCKET,
    GCP_STATIC_BUCKET: process.env.GOOGLE_CLOUD_STATIC_BUCKET
  }
};

export default nextConfig;
```

### 2. Create GCP storage utility

```typescript
// app/utils/gcp-storage.ts
import { Storage } from '@google-cloud/storage';

const storage = new Storage({
  projectId: process.env.GOOGLE_CLOUD_PROJECT,
  keyFilename: process.env.GOOGLE_APPLICATION_CREDENTIALS
});

export const contextsBucket = storage.bucket(process.env.GOOGLE_CLOUD_BUCKET!);
export const staticBucket = storage.bucket(process.env.GOOGLE_CLOUD_STATIC_BUCKET!);

export async function uploadContext(domain: string, filename: string, content: string) {
  const file = contextsBucket.file(`${domain}/${filename}`);
  await file.save(content, {
    metadata: {
      contentType: 'text/plain',
      cacheControl: 'public, max-age=3600'
    }
  });
}

export async function getContextUrl(domain: string, filename: string): Promise<string> {
  const file = contextsBucket.file(`${domain}/${filename}`);
  const [url] = await file.getSignedUrl({
    action: 'read',
    expires: Date.now() + 24 * 60 * 60 * 1000 // 24 hours
  });
  return url;
}
```

## 🚀 Deployment Options

### Option 1: Cloud Run (Recommended)

#### 1. Create Dockerfile

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy application
COPY . .

# Build application
RUN npm run build

# Expose port
EXPOSE 3000

# Start application
CMD ["npm", "start"]
```

#### 2. Create .dockerignore

```
node_modules
.next
.git
.env*
gcp-credentials.json
```

#### 3. Deploy to Cloud Run

```bash
# Build and deploy
gcloud run deploy cmbagent-info \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID \
  --set-env-vars GOOGLE_CLOUD_BUCKET=YOUR_PROJECT_ID-contexts

# Get the URL
gcloud run services describe cmbagent-info --region us-central1 --format="value(status.url)"
```

### Option 2: Static Hosting on Cloud Storage

#### 1. Build static site

```bash
# Build for static export
npm run build

# Upload to static bucket
gsutil -m rsync -r -d out/ gs://YOUR_PROJECT_ID-static/

# Set website configuration
gsutil web set -m index.html -e 404.html gs://YOUR_PROJECT_ID-static
```

#### 2. Configure custom domain (optional)

```bash
# Map custom domain
gsutil web set -m index.html gs://YOUR_PROJECT_ID-static
```

## 🔄 Automated Context Updates

### 1. Update auto-update script for GCP

The existing `auto-update-contexts.py` script already supports GCP. Just ensure:

```bash
# Set environment variables
export GOOGLE_APPLICATION_CREDENTIALS=./gcp-credentials.json
export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID

# Run the updater
python scripts/auto-update-contexts.py once
```

### 2. Deploy updater as Cloud Function

Create `functions/context-updater/main.py`:

```python
import functions_framework
from google.cloud import storage
import subprocess
import os

@functions_framework.http
def update_contexts(request):
    """HTTP Cloud Function to update contexts."""
    
    # Set environment
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/tmp/credentials.json'
    
    # Run update
    result = subprocess.run([
        'python', '/workspace/scripts/auto-update-contexts.py', 'once'
    ], capture_output=True, text=True)
    
    return {
        'status': 'success' if result.returncode == 0 else 'error',
        'output': result.stdout,
        'error': result.stderr
    }
```

Deploy function:

```bash
# Deploy function
gcloud functions deploy context-updater \
  --runtime python39 \
  --trigger-http \
  --allow-unauthenticated \
  --region us-central1

# Set up Cloud Scheduler
gcloud scheduler jobs create http context-update-job \
  --schedule="0 * * * *" \
  --uri="YOUR_FUNCTION_URL" \
  --http-method=POST
```

## 📊 Monitoring and Logging

### 1. Enable Cloud Monitoring

```bash
# Enable monitoring APIs
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com
```

### 2. Create monitoring dashboard

```bash
# Create uptime check
gcloud monitoring uptime-checks create http cmbagent-info \
  --display-name="CMB Agent Info Uptime" \
  --uri="YOUR_SITE_URL" \
  --period=60s
```

## 🔒 Security Best Practices

### 1. IAM Roles

```bash
# Create minimal service account for app
gcloud iam service-accounts create cmbagent-app \
  --display-name="CMB Agent App Service Account"

# Grant minimal permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:cmbagent-app@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"
```

### 2. Network Security

```bash
# Create VPC connector (if needed)
gcloud compute networks vpc-access connectors create cmbagent-connector \
  --network=default \
  --region=us-central1 \
  --range=10.8.0.0/28
```

## 💰 Cost Optimization

### 1. Storage classes

```bash
# Set lifecycle policy for cost optimization
gsutil lifecycle set lifecycle.json gs://YOUR_PROJECT_ID-contexts
```

Create `lifecycle.json`:

```json
{
  "rule": [
    {
      "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
      "condition": {
        "age": 30,
        "matchesStorageClass": ["STANDARD"]
      }
    },
    {
      "action": {"type": "Delete"},
      "condition": {
        "age": 365,
        "matchesStorageClass": ["NEARLINE"]
      }
    }
  ]
}
```

### 2. Cloud Run scaling

```bash
# Set minimum instances to 0 for cost savings
gcloud run services update cmbagent-info \
  --region us-central1 \
  --min-instances 0 \
  --max-instances 10
```

## 🚀 Quick Start Commands

```bash
# 1. Setup project
gcloud init
gcloud config set project YOUR_PROJECT_ID

# 2. Enable APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com storage.googleapis.com

# 3. Create buckets
gsutil mb gs://YOUR_PROJECT_ID-contexts
gsutil mb gs://YOUR_PROJECT_ID-static

# 4. Setup credentials
gcloud iam service-accounts create context-updater --display-name="Context Updater"
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID --member="serviceAccount:context-updater@YOUR_PROJECT_ID.iam.gserviceaccount.com" --role="roles/storage.objectAdmin"
gcloud iam service-accounts keys create gcp-credentials.json --iam-account=context-updater@YOUR_PROJECT_ID.iam.gserviceaccount.com

# 5. Deploy
gcloud run deploy cmbagent-info --source . --platform managed --region us-central1 --allow-unauthenticated

# 6. Setup automation
python scripts/auto-update-contexts.py once
```

## 📞 Support

- **GCP Documentation**: https://cloud.google.com/docs
- **Cloud Storage**: https://cloud.google.com/storage/docs
- **Cloud Run**: https://cloud.google.com/run/docs
- **IAM**: https://cloud.google.com/iam/docs

Your site is now ready for production deployment on GCP! 🎉 