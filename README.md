DEPRECATED IN FAVOR OF MONOREPO

# Bijak Mengeluh - Backend

AWS Lambda backend for AI complaint generation and agency matching.

---

## Quick Start

```bash
# Setup secrets (first time)
./scripts/setup-secrets.sh

# Deploy
sam build && sam deploy
```

---

## Features

- AI text generation (Bedrock Claude)
- Agency matching (DynamoDB keyword index)
- Social media discovery
- Parallel processing (4-6s response)

---

## Stack

- AWS Lambda (Python 3.12)
- AWS Bedrock (Claude 3 Haiku)
- DynamoDB (keyword index)
- API Gateway

---

## API

```bash
curl -X POST https://brain.bijakmengeluh.id/generate \
  -H "Content-Type: application/json" \
  -d '{"complaint": "Jalan rusak", "tone": "formal"}'
```

---

**See parent README for full documentation**
