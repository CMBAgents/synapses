# Context Generation and Synchronization Guide

This guide explains how to use the automatic context generation and cloud storage system for GitHub repository documentation.

## 🚀 Installation

### 1. Automatic dependency installation

```bash
python scripts/install-dependencies.py
```

This script will:
- Check Python version (3.8+ required)
- Install necessary Python packages (including `contextmaker`)
- Verify Git is installed (required for cloning repositories)
- Install Node.js dependencies
- Create necessary directories
- Configure configuration files

### 2. Configuration

#### Environment variables (.env)

Create a `.env` file at the project root:

```env
# GitHub Token (optional, to increase rate limiting limits)
GITHUB_TOKEN=your_github_token_here

# AWS Configuration (for S3)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key

# Google Cloud Configuration (for GCS)
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# Cloud configuration
CLOUD_PROVIDER=local  # local, s3, gcs, http
CLOUD_BUCKET=cmbagent-contexts
CLOUD_REGION=us-east-1
```

#### Cloud Configuration (cloud-config.json)

Modify `cloud-config.json` according to your needs:

```json
{
  "provider": "local",
  "bucket_name": "cmbagent-contexts",
  "region": "us-east-1",
  "sync_enabled": true,
  "backup_enabled": true,
  "cdn_url": null,
  "upload_url": null
}
```

**Supported providers:**
- `local`: Local storage in `public/context/`
- `s3`: Amazon S3
- `gcs`: Google Cloud Storage
- `http`: Custom REST API

## 📋 Usage

### Complete pipeline

To run the complete pipeline (recommended):

```bash
python scripts/generate-and-sync-all.py
```

### Individual commands

```bash
# Update library data from ASCL
python scripts/generate-and-sync-all.py update-data

# Generate missing contexts
python scripts/generate-and-sync-all.py generate

# Synchronize to cloud
python scripts/generate-and-sync-all.py sync

# Build contexts for application
python scripts/generate-and-sync-all.py build

# Validate generated contexts
python scripts/generate-and-sync-all.py validate
```

### Individual scripts

```bash
# Generate missing contexts
python scripts/generate-missing-contexts.py

# Synchronize to cloud
python scripts/cloud-sync-contexts.py

# Build contexts
node scripts/build-context.js
```

## 🔧 Detailed configuration

### 1. AWS S3 Configuration

```json
{
  "provider": "s3",
  "bucket_name": "your-s3-bucket",
  "region": "us-east-1",
  "sync_enabled": true
}
```

Required environment variables:
```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

### 2. Google Cloud Storage Configuration

```json
{
  "provider": "gcs",
  "bucket_name": "your-gcs-bucket",
  "sync_enabled": true
}
```

Required environment variables:
```env
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
```

### 3. REST API Configuration

```json
{
  "provider": "http",
  "upload_url": "https://api.example.com/upload",
  "sync_enabled": true
}
```

## 📊 File structure

```
app/
├── context/
│   ├── astronomy/
│   │   ├── astropy-context.txt
│   │   ├── healpy-context.txt
│   │   └── ...
│   └── finance/
│       ├── yfinance-context.txt
│       └── ...
├── data/
│   ├── astronomy-libraries.json
│   ├── finance-libraries.json
│   └── libraries.json
public/
└── context/
    ├── astropy-context.txt
    ├── healpy-context.txt
    └── ...
```

## 🔍 Generation process

### 1. ASCL data extraction

The system automatically retrieves GitHub repositories from ASCL (Astrophysics Source Code Library) and filters them according to relevant keywords.

### 2. Context generation with contextmaker

For each repository:
1. Extract repository information (owner/repo) from GitHub URL
2. **Clone repository** with `git clone`
3. Use the `contextmaker` package to extract all documentation from the cloned repo
4. Generate a complete context file with all documentation
5. Add metadata and structured saving

### 3. Cloud synchronization

Generated contexts are:
1. Saved locally
2. Copied to `public/context/`
3. Uploaded to the configured cloud service
4. Metadata updated

## 📈 Monitoring and logs

### Log files

- `context_generation.log`: Context generation logs
- `cloud_sync.log`: Cloud synchronization logs
- `generate_and_sync.log`: Complete pipeline logs

### Execution report

After each execution, an `execution_report.json` file is generated with:
- Date and execution duration
- Statistics (contexts generated, synchronized, errors)
- Configuration used

## 🛠️ Troubleshooting

### Common errors

1. **GitHub rate limiting**:
   - Add a GitHub token in `.env`
   - Increase delays in configuration

2. **Cloud permission errors**:
   - Check AWS/GCS credentials
   - Check bucket permissions

3. **Empty context files**:
   - Check that repositories exist
   - Check for documentation presence

### Diagnostic commands

```bash
# Check configuration
python scripts/validate-config.js

# Test GitHub connection
python -c "import requests; print(requests.get('https://api.github.com/rate_limit').json())"

# List existing contexts
find app/context -name "*.txt" | wc -l
```

## 🔄 Automation

### Cron job (Linux/Mac)

Add to your crontab:

```bash
# Daily generation at 2 AM
0 2 * * * cd /path/to/cmbagent-info && python scripts/generate-and-sync-all.py
```

### GitHub Actions

Create `.github/workflows/context-generation.yml`:

```yaml
name: Generate Contexts

on:
  schedule:
    - cron: '0 2 * * *'
  workflow_dispatch:

jobs:
  generate-contexts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: python scripts/install-dependencies.py
      - run: python scripts/generate-and-sync-all.py
```

## 📚 API and integration

### Available endpoints

- `GET /api/generate-all-contexts`: Triggers generation
- `GET /api/update-context`: Updates a specific context
- `GET /api/context/[programId]`: Retrieves a context

### Integration with other systems

The system can be integrated with:
- CI/CD pipelines
- Monitoring systems
- Backup systems
- CDN services

## 🤝 Contribution

To contribute to the system:

1. Fork the repository
2. Create a branch for your feature
3. Add tests
4. Submit a pull request

### Tests

```bash
# Unit tests
python -m pytest tests/

# Integration tests
python scripts/test-integration.py
```

## 📞 Support

For any questions or issues:
1. Check logs in `.log` files
2. Verify configuration in `cloud-config.json`
3. Test with diagnostic commands
4. Open an issue on GitHub

---

**Note:** This system is designed to be robust and scalable. It automatically handles errors, rate limits, and backups to ensure the reliability of your contexts. 