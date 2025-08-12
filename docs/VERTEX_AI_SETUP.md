# Vertex AI Integration Setup

This document explains how to set up and use Google Cloud Vertex AI with your LLM system.

## Prerequisites

1. **Google Cloud Project**: You need an active Google Cloud project
2. **Vertex AI API**: The Vertex AI API must be enabled in your project
3. **Service Account**: A service account with appropriate permissions
4. **Authentication**: Proper authentication setup

## Setup Steps

### 1. Enable Vertex AI API

```bash
gcloud services enable aiplatform.googleapis.com
```

### 2. Create a Service Account

```bash
# Create service account
gcloud iam service-accounts create vertex-ai-user \
    --display-name="Vertex AI User"

# Grant necessary roles
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:vertex-ai-user@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# Create and download key
gcloud iam service-accounts keys create vertex-ai-key.json \
    --iam-account=vertex-ai-user@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

### 3. Set Environment Variables

Set the following environment variables:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/vertex-ai-key.json"
export GOOGLE_CLOUD_PROJECT="your-project-id"
export VERTEX_AI_LOCATION="us-central1"
export VERTEX_AI_ENDPOINT="us-central1-aiplatform.googleapis.com"
```

### 4. Install Dependencies

```bash
npm install @google-cloud/aiplatform
```

## Available Models

The following Vertex AI models are available:

- **`vertexai/gemini-1.5-flash`**: Fast and efficient model for quick responses
- **`vertexai/gemini-1.5-pro`**: More capable model for complex tasks

## Usage

Once configured, you can use Vertex AI models just like any other model in your system:

```typescript
// The system will automatically detect Vertex AI models
const modelId = "vertexai/gemini-1.5-flash";
const response = await createChatCompletion(modelId, messages, options);
```

## Configuration

Vertex AI models are configured in `config.json` with the following options:

- `temperature`: Controls randomness (0.0 to 1.0)
- `max_completion_tokens`: Maximum tokens to generate
- `stream`: Currently set to false for Vertex AI (streaming support is limited)

## Troubleshooting

### Common Issues

1. **Authentication Error**: Ensure `GOOGLE_APPLICATION_CREDENTIALS` is set correctly
2. **Project Not Found**: Verify `GOOGLE_CLOUD_PROJECT` is correct
3. **API Not Enabled**: Make sure Vertex AI API is enabled in your project
4. **Permission Denied**: Check that your service account has the `aiplatform.user` role

### Debug Mode

Enable debug logging by setting:

```bash
export DEBUG=vertex-ai:*
```

## Cost Considerations

- Vertex AI pricing is based on input/output tokens
- Gemini 1.5 Flash is generally more cost-effective than Pro
- Monitor usage through Google Cloud Console

## Security Notes

- Never commit service account keys to version control
- Use IAM roles with minimal required permissions
- Consider using Workload Identity for production deployments
