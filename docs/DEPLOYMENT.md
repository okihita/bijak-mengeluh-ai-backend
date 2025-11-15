# Deployment Guide

Complete guide for deploying Bijak Mengeluh Backend.

---

## Prerequisites

### Required Software
- AWS CLI configured with profile `bijak-mengeluh-aws-iam`
- SAM CLI installed
- Python 3.12

### Required AWS Resources
- ACM Certificate in ap-southeast-2
- Bedrock model access enabled
- IAM permissions for SSM Parameter Store

### External Services
- Pinecone index (or DynamoDB table for v1.3.0+)
- Serper.dev API key

---

## Quick Deploy

```bash
# 1. Configure API keys (first time only)
./scripts/setup-secrets.sh

# 2. Deploy
./scripts/deploy.sh
```

---

## Step-by-Step Deployment

### 1. Configure API Keys

Store API keys in AWS Systems Manager Parameter Store:

```bash
# Pinecone API key
aws ssm put-parameter \
  --name /bijak-mengeluh/pinecone-api-key \
  --value "YOUR_KEY" \
  --type SecureString \
  --profile bijak-mengeluh-aws-iam \
  --region ap-southeast-2

# Serper API key
aws ssm put-parameter \
  --name /bijak-mengeluh/serper-api-key \
  --value "YOUR_KEY" \
  --type SecureString \
  --profile bijak-mengeluh-aws-iam \
  --region ap-southeast-2
```

### 2. Validate Template

```bash
sam validate --profile bijak-mengeluh-aws-iam
```

### 3. Build

```bash
sam build --profile bijak-mengeluh-aws-iam
```

### 4. Deploy

```bash
sam deploy --profile bijak-mengeluh-aws-iam
```

For first-time deployment:

```bash
sam deploy --profile bijak-mengeluh-aws-iam --guided
```

---

## Infrastructure Overview

### Resources Created

#### Lambda Functions
- **Main Function:** Complaint generation and orchestration (768MB, 60s timeout)
- **Finder Function:** Social media handle lookup (512MB, 30s timeout)

#### DynamoDB Tables
- **Social Cache:** Stores verified social media handles
- **Agencies:** Ministry/agency data with embeddings (v1.3.0+)

#### API Gateway
- **Type:** HTTP API
- **Custom Domain:** brain.bijakmengeluh.id
- **CORS:** Enabled for frontend domains

#### IAM Roles
- Lambda execution roles with Bedrock, DynamoDB, and Lambda invoke permissions

---

## Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `PineconeApiKey` | Pinecone API key | From SSM |
| `PineconeIndexName` | Pinecone index name | `2025-aws-hackathon` |
| `SerperApiKey` | Serper.dev API key | From SSM |
| `CacheTableName` | DynamoDB cache table | `BijakMengeluhSocialsCacheTable` |
| `BrandedApiDomainName` | Custom domain | `brain.bijakmengeluh.id` |

---

## Post-Deployment

### Get API Endpoint

```bash
aws cloudformation describe-stacks \
  --stack-name cloudformation-stack-2025-aws-hackathon-bijak-mengeluh \
  --query 'Stacks[0].Outputs' \
  --profile bijak-mengeluh-aws-iam \
  --region ap-southeast-2
```

### Test API

```bash
curl -X POST https://brain.bijakmengeluh.id/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Jalan rusak di depan rumah"}'
```

### View Logs

```bash
sam logs -n BijakMengeluhComplaintGenerationFunction \
  --stack-name cloudformation-stack-2025-aws-hackathon-bijak-mengeluh \
  --profile bijak-mengeluh-aws-iam --tail
```

---

## Troubleshooting

### Custom Domain Already Mapped
**Error:** Domain is already mapped to another API  
**Solution:** Remove existing mapping or use different domain

### Certificate Not Found
**Error:** Certificate ARN not found  
**Solution:** Ensure certificate exists in ap-southeast-2 region

### Bedrock Access Denied
**Error:** Access denied to Bedrock models  
**Solution:** Request model access in AWS Bedrock console

### Pinecone Connection Failed
**Error:** Cannot connect to Pinecone  
**Solution:** Verify API key and index name in Parameter Store

---

## Rollback

If deployment fails:

```bash
sam delete --stack-name cloudformation-stack-2025-aws-hackathon-bijak-mengeluh \
  --profile bijak-mengeluh-aws-iam \
  --region ap-southeast-2
```

Then fix issues and redeploy.

---

## Required IAM Permissions

Your IAM user needs:

- **SSM:** `ssm:PutParameter`, `ssm:GetParameter`
- **CloudFormation:** `cloudformation:*`
- **Lambda:** `lambda:CreateFunction`, `lambda:UpdateFunctionCode`
- **API Gateway:** `apigateway:*`
- **DynamoDB:** `dynamodb:CreateTable`, `dynamodb:DescribeTable`
- **IAM:** `iam:CreateRole`, `iam:AttachRolePolicy`, `iam:PassRole`

---

## Monitoring

### CloudWatch Metrics
- Lambda Duration
- Lambda Errors
- Lambda Concurrent Executions
- API Gateway 4xx/5xx errors
- DynamoDB throttles

### Custom Metrics
- Response time (X-Processing-Time header)
- Ministry match accuracy
- Cache hit rate

### Alarms
Set up CloudWatch alarms for:
- Lambda errors > 5 in 5 minutes
- API Gateway 5xx > 10 in 5 minutes
- Lambda duration > 10 seconds

---

## Cost Optimization

### Current Costs (v1.3.0)
- Lambda: ~$10/month (1000 requests/day)
- DynamoDB: ~$5/month
- API Gateway: ~$3/month
- Bedrock: ~$15/month
- **Total:** ~$33/month

### Optimization Tips
- Use DynamoDB instead of Pinecone (saves $65/month)
- Reduce Lambda memory if response time acceptable
- Enable DynamoDB auto-scaling
- Cache common embeddings
- Use provisioned concurrency only if needed

---

## Security Best Practices

- Store all secrets in SSM Parameter Store (SecureString)
- Use least-privilege IAM roles
- Enable CloudTrail for audit logging
- Implement rate limiting
- Validate all user inputs
- Use HTTPS only
- Enable API Gateway access logging
- Rotate API keys regularly

---

## Backup & Disaster Recovery

### DynamoDB Backups
- Enable point-in-time recovery
- Create on-demand backups before major changes
- Test restore procedures

### Code Backups
- Git repository is source of truth
- Tag releases in Git
- Keep SAM templates in version control

### Recovery Time Objective (RTO)
- Target: < 1 hour
- Procedure: Redeploy from Git using SAM

### Recovery Point Objective (RPO)
- Target: < 5 minutes
- DynamoDB point-in-time recovery provides this
