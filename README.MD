
# Bijak Mengeluh AI Backend

## Overview
This repository contains AWS Lambda functions and associated resources for the Bijak Mengeluh complaint generation system.

## How It Works

The backend processes user complaints through the following workflow:

1. **User Input** → User submits a complaint via API
2. **Embedding Generation** → Text is converted to vector embedding using AWS Bedrock (Cohere multilingual model)
3. **Ministry Matching** → Pinecone vector database finds the top 3 most relevant government ministries
4. **Complaint Generation** → AWS Bedrock (Claude 3 Haiku) generates a formal, polished complaint text
5. **Rationale Generation** → System explains why the top ministry was selected
6. **Social Handle Lookup** → Retrieves ministry's social media handle:
   - First checks DynamoDB cache
   - If not cached, invokes finder Lambda function
   - High-confidence results are cached for future use
7. **Response** → Returns generated complaint, suggested ministries, rationale, and social media handle

### Key Components
- **Main Lambda**: Orchestrates the entire complaint processing flow
- **Finder Lambda**: Searches for ministry social media handles
- **Pinecone**: Vector database storing ministry embeddings
- **DynamoDB**: Caches verified social media handles
- **AWS Bedrock**: Provides AI models for embeddings and text generation

## Structure
- `/src` - Source code for Lambda functions
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