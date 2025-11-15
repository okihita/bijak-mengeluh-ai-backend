# Bijak Mengeluh - Backend

> 🧠 AI processing engine for complaint generation and ministry matching

**Part of the Bijak Mengeluh ecosystem** | [Frontend Repo](https://github.com/okihita/aic-complaint-app)

---

## Overview

AWS Lambda-based backend that transforms casual Indonesian complaints into formal government submissions with AI-powered ministry matching.

**How it works:**
1. User submits casual complaint → 2. AI generates formal text + finds relevant ministries → 3. Returns polished complaint with contact info

### Tech Stack
- **AWS Lambda** (Python 3.12) - Serverless compute
- **AWS Bedrock** - Claude 3 Haiku for text generation, Cohere for embeddings
- **Pinecone** - Vector database for ministry matching
- **DynamoDB** - Social media handle cache
- **API Gateway** - HTTPS endpoint

### Performance
- **Response time:** 4-6 seconds (50% faster via parallel processing)
- **Cold start:** 2-3 seconds
- **Accuracy:** 90%+ ministry match relevance

---

## Quick Start

### Prerequisites
- AWS CLI with profile `bijak-mengeluh-aws-iam`
- SAM CLI
- Python 3.12

### Setup & Deploy
```bash
# 1. Configure API keys (first time only)
./scripts/setup-secrets.sh

# 2. Deploy
./scripts/deploy.sh
```

### API Usage
```bash
curl -X POST https://brain.bijakmengeluh.id/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Jalanan depan rumah rusak parah udah 3 bulan"}'
```

**Response:**
```json
{
  "generated_text": "Kepada Yth. Kementerian PUPR...",
  "suggested_contacts": [
    {"name": "Kementerian PUPR", "score": 0.95, "description": "..."}
  ],
  "rationale": "PUPR handles road infrastructure...",
  "social_handle_info": {"handle": "@kemenPUPR", "status": "verified"}
}
```

---

## Project Structure

```
├── src/
│   ├── handlers/          # Lambda entry points
│   ├── services/          # Business logic (Bedrock, Pinecone, Social)
│   ├── config/            # Prompts and configuration
│   └── models/            # Data models
├── scripts/               # Deployment and utilities
├── template.yaml          # SAM infrastructure template
└── docs/                  # Documentation
```

---

## Development

### Local Testing
```bash
sam local invoke BijakMengeluhComplaintGenerationFunction \
  --event events/test-event.json \
  --profile bijak-mengeluh-aws-iam
```

### View Logs
```bash
sam logs -n BijakMengeluhComplaintGenerationFunction \
  --stack-name cloudformation-stack-2025-aws-hackathon-bijak-mengeluh \
  --profile bijak-mengeluh-aws-iam --tail
```

### Monitoring
CloudWatch metrics to watch:
- Lambda Duration & Errors
- API Gateway 4xx/5xx
- DynamoDB throttles

---

## Architecture

### Parallel Processing Flow
```
User Input
    ↓
┌───────────────────────────┐
│  Generate Embedding       │ (sequential)
└───────────────────────────┘
    ↓
┌───────────────────────────┐
│  Search Ministries        │ (sequential)
└───────────────────────────┘
    ↓
┌─────────────────┬─────────────────┐
│ Generate Text   │ Generate Embed  │ (parallel)
└─────────────────┴─────────────────┘
    ↓
┌─────────────────┬─────────────────┐
│ Get Rationale   │ Find Social     │ (parallel)
└─────────────────┴─────────────────┘
    ↓
Response
```

### Key Design Decisions
- **Parallel processing:** Independent operations run concurrently (ThreadPoolExecutor)
- **Increased memory:** 1024MB main Lambda = more CPU = faster execution
- **Indonesian errors:** Better UX for local users
- **DynamoDB cache:** Reduces repeated social media lookups

---

## Documentation

- [CHANGELOG.md](./docs/CHANGELOG.md) - Development history
- [ROADMAP.md](./docs/ROADMAP.md) - Future plans
- [DEPLOYMENT.md](./docs/DEPLOYMENT.md) - Detailed deployment guide

---

## Contributing

1. Create feature branch
2. Test locally with `sam local invoke`
3. Deploy to dev environment
4. Submit pull request

---

## License

Proprietary - Bijak Mengeluh Project
