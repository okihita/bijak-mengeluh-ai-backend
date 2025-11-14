
# Bijak Mengeluh AI Backend

## Overview
This repository contains AWS Lambda functions and associated resources for the Bijak Mengeluh complaint generation system.

## Recent Updates (Phase 1 - Nov 2025)

### Performance Improvements
- ⚡ **50% faster response times** through parallel processing
- 🚀 **Increased Lambda memory** (1024MB) for better performance
- 🔄 **Concurrent execution** of independent operations
- 📊 **Performance monitoring** with X-Processing-Time headers

### Error Handling
- 🇮🇩 **Indonesian error messages** for better user experience
- ✅ **Input validation** on server side
- 🛡️ **Graceful error handling** with proper HTTP status codes

See [PHASE1_DEPLOYMENT.md](./PHASE1_DEPLOYMENT.md) for detailed changes.

## How It Works

The backend processes user complaints through the following workflow:

1. **User Input** → User submits a complaint via API
2. **Parallel Processing** → Embedding generation and text generation run concurrently
3. **Ministry Matching** → Pinecone vector database finds the top 3 most relevant government ministries
4. **Complaint Generation** → AWS Bedrock (Claude 3 Haiku) generates a formal, polished complaint text
5. **Rationale & Social Lookup** → System explains ministry selection and finds social media handles (parallel)
6. **Response** → Returns generated complaint, suggested ministries, rationale, and social media handle

### Key Components
- **Main Lambda** (1024MB): Orchestrates the entire complaint processing flow with parallel execution
- **Finder Lambda** (768MB): Searches for ministry social media handles
- **Pinecone**: Vector database storing ministry embeddings
- **DynamoDB**: Caches verified social media handles
- **AWS Bedrock**: Provides AI models for embeddings and text generation

## Performance Metrics

- **Average Response Time:** 4-6 seconds (50% improvement)
- **Cold Start:** 2-3 seconds
- **Parallel Operations:** Save 3-4 seconds per request

## Structure
- `/src` - Source code for Lambda functions
  - `/handlers` - Lambda entry points
  - `/services` - Business logic (Bedrock, Pinecone, Social Lookup)
  - `/config` - Configuration and prompts
  - `/models` - Data models
- `/scripts` - Deployment and utility scripts
- `/template.yaml` - SAM template for infrastructure

## Prerequisites
- AWS Account with appropriate IAM permissions
- AWS CLI configured with profile `bijak-mengeluh-aws-iam`
- SAM CLI installed
- Python 3.12 (matches AWS Lambda runtime)

## Setup

### 1. Configure API Keys
API keys are stored securely in AWS Systems Manager Parameter Store.

**First time setup:**
```bash
./scripts/setup-secrets.sh
```

See [SETUP.md](SETUP.md) for detailed instructions on managing API keys.

### 2. Deploy
```bash
./scripts/deploy.sh
```

Or manually:
```bash
sam build --profile bijak-mengeluh-aws-iam
sam deploy --profile bijak-mengeluh-aws-iam
```

## API Endpoint

**Production:** https://brain.bijakmengeluh.id/generate

### Request
```json
{
  "prompt": "Jalanan depan rumah gue di Palmerah ancur banget udah 3 bulan..."
}
```

### Response
```json
{
  "generated_text": "Formal complaint text...",
  "suggested_contacts": [
    {
      "name": "Ministry Name",
      "score": 0.95,
      "description": "Ministry description"
    }
  ],
  "rationale": "Explanation for ministry selection...",
  "social_handle_info": {
    "handle": "@ministry_handle",
    "status": "verified"
  }
}
```

## Monitoring

Monitor these CloudWatch metrics:
- Lambda Duration
- Lambda Errors
- Lambda Concurrent Executions
- API Gateway 4xx/5xx errors

## Development

### Local Testing
```bash
sam local invoke BijakMengeluhComplaintGenerationFunction \
  --event events/test-event.json \
  --profile bijak-mengeluh-aws-iam
```

### Logs
```bash
sam logs -n BijakMengeluhComplaintGenerationFunction \
  --stack-name cloudformation-stack-2025-aws-hackathon-bijak-mengeluh \
  --profile bijak-mengeluh-aws-iam \
  --tail
```

## Architecture Decisions

### Why Parallel Processing?
- Ministry search and text generation are independent
- Rationale and social lookup can run concurrently
- ThreadPoolExecutor is safe for I/O-bound operations
- Reduces total response time by ~50%

### Why Increased Memory?
- More memory = more CPU in Lambda
- Faster execution for AI model invocations
- Better cold start performance
- Cost increase is minimal for the performance gain

## Troubleshooting

### Slow Response Times
- Check CloudWatch metrics for Lambda duration
- Verify Bedrock model availability
- Check Pinecone index health

### Error Messages
All errors are now in Indonesian for better UX:
- "Keluhan belum diisi" - Missing prompt
- "Keluhan terlalu pendek" - Too short (< 20 chars)
- "Ada masalah di server" - Internal error

## Contributing

1. Create feature branch
2. Make changes
3. Test locally with `sam local invoke`
4. Deploy to dev environment
5. Create pull request

## License

Proprietary - Bijak Mengeluh Project