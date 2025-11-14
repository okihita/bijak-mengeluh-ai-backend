# Deployment Guide

## Prerequisites

### Required Software
- AWS CLI configured with profile `bijak-mengeluh-aws-iam`
- SAM CLI installed
- Python 3.12

### Required AWS Resources
1. ✅ ACM Certificate in ap-southeast-2
   - ARN: `arn:aws:acm:ap-southeast-2:986517526233:certificate/ccf38539-1caa-4ae9-8f86-70ab1b4408c0`
2. ⚠️  Route53 hosted zone for `bijakmengeluh.id` (if using custom domain)
3. ✅ Bedrock model access enabled in ap-southeast-2
4. ✅ IAM permissions for SSM Parameter Store

### External Services
1. ✅ Pinecone index created and populated with ministry embeddings
2. ✅ Serper.dev API key obtained

---

## Step 1: Configure API Keys

API keys are stored securely in AWS Systems Manager Parameter Store.

### Automated Setup

```bash
./scripts/setup-secrets.sh
```

### Manual Setup

```bash
# Store Pinecone API key
aws ssm put-parameter \
  --name /bijak-mengeluh/pinecone-api-key \
  --value "YOUR_PINECONE_API_KEY" \
  --type SecureString \
  --description "Pinecone API key for Bijak Mengeluh project" \
  --profile bijak-mengeluh-aws-iam \
  --region ap-southeast-2

# Store Serper API key
aws ssm put-parameter \
  --name /bijak-mengeluh/serper-api-key \
  --value "YOUR_SERPER_API_KEY" \
  --type SecureString \
  --description "Serper API key for Bijak Mengeluh project" \
  --profile bijak-mengeluh-aws-iam \
  --region ap-southeast-2
```

### View Stored Keys

```bash
# View Pinecone key
aws ssm get-parameter \
  --name /bijak-mengeluh/pinecone-api-key \
  --with-decryption \
  --query Parameter.Value \
  --output text \
  --profile bijak-mengeluh-aws-iam \
  --region ap-southeast-2
```

### Update Keys

```bash
# Add --overwrite flag to update
aws ssm put-parameter \
  --name /bijak-mengeluh/pinecone-api-key \
  --value "NEW_KEY" \
  --type SecureString \
  --overwrite \
  --profile bijak-mengeluh-aws-iam \
  --region ap-southeast-2
```

---

## Step 2: Validate Template

```bash
sam validate --profile bijak-mengeluh-aws-iam
```

Expected output: `template.yaml is a valid SAM Template`

---

## Step 3: Build

```bash
sam build --profile bijak-mengeluh-aws-iam
```

---

## Step 4: Deploy

### Automated Deployment

```bash
./scripts/deploy.sh
```

### Manual Deployment

```bash
sam deploy --profile bijak-mengeluh-aws-iam
```

### First-Time Deployment (Guided)

```bash
sam deploy --profile bijak-mengeluh-aws-iam --guided
```

You'll be prompted for:
- Stack name
- AWS Region (ap-southeast-2)
- Parameter values (API keys retrieved from Parameter Store)
- Confirm changes before deploy
- Allow SAM CLI IAM role creation

---

## Infrastructure Overview

### Resources Created

#### 1. DynamoDB Table
- **Name**: `BijakMengeluhSocialsCacheTable`
- **Purpose**: Caches verified social media handles
- **Billing**: PAY_PER_REQUEST (serverless)
- **Key**: `ministry_name` (String)

#### 2. HTTP API Gateway
- **Name**: `ComplaintGenerationHttpApi`
- **Features**:
  - CORS enabled for `localhost:3000` and `bijakmengeluh.id`
  - Custom domain: `brain.bijakmengeluh.id`
  - SSL certificate attached
  - Regional endpoint

#### 3. Main Lambda Function
- **Name**: `BijakMengeluhComplaintGenerationFunction`
- **Runtime**: Python 3.12
- **Memory**: 512 MB
- **Timeout**: 60 seconds
- **Handler**: `handlers.complaint_handler.lambda_handler`
- **Permissions**:
  - Bedrock model invocation
  - DynamoDB read/write
  - Invoke social finder Lambda
- **Endpoint**: `POST /generate`

#### 4. Social Finder Lambda
- **Name**: `BijakMengeluhSocialFinderFunction`
- **Runtime**: Python 3.12
- **Memory**: 512 MB
- **Timeout**: 30 seconds
- **Handler**: `handlers.social_finder_handler.lambda_handler`
- **Permissions**: Bedrock model invocation

### Auto-Generated Resources
SAM automatically creates:
- IAM Roles for Lambda functions
- Lambda permissions for API Gateway
- CloudWatch Log Groups
- API Gateway stages and deployments
- Custom domain mapping

---

## Deployment Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `PineconeApiKey` | Pinecone API key | Retrieved from SSM |
| `PineconeIndexName` | Pinecone index name | `2025-aws-hackathon` |
| `SerperApiKey` | Serper.dev API key | Retrieved from SSM |
| `CacheTableName` | DynamoDB table name | `BijakMengeluhSocialsCacheTable` |
| `BrandedApiDomainName` | Custom domain | `brain.bijakmengeluh.id` |
| `BrandedApiDomainCertificateArn` | ACM certificate ARN | (see Prerequisites) |

---

## Validation Checklist

✅ **Template is valid** (sam validate passed)  
✅ **All required resources defined**  
✅ **IAM permissions properly scoped**  
✅ **Environment variables configured**  
✅ **CORS properly configured**  
✅ **API keys stored in Parameter Store**  

---

## Clean Deployment (From Scratch)

If the CloudFormation stack is deleted, redeploying will:

1. ✅ Create new DynamoDB table (⚠️ cached data will be lost)
2. ✅ Create new API Gateway
3. ✅ Create new Lambda functions with fresh code
4. ✅ Create new IAM roles
5. ✅ Re-establish custom domain mapping
6. ⚠️  May require manual Route53 update if domain mapping changes

---

## Troubleshooting

### Issue: Custom Domain Already Mapped
**Error**: Domain is already mapped to another API  
**Solution**: Remove existing mapping or use different domain

### Issue: Certificate Not Found
**Error**: Certificate ARN not found  
**Solution**: Ensure certificate exists in ap-southeast-2 region

### Issue: Pinecone Connection Failed
**Error**: Cannot connect to Pinecone  
**Solution**: Verify API key and index name in Parameter Store

### Issue: Bedrock Access Denied
**Error**: Access denied to Bedrock models  
**Solution**: Request model access in AWS Bedrock console

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
sam logs --stack-name cloudformation-stack-2025-aws-hackathon-bijak-mengeluh \
  --profile bijak-mengeluh-aws-iam \
  --region ap-southeast-2
```

---

## Required IAM Permissions

Your IAM user needs:

**SSM Parameter Store**:
- `ssm:PutParameter`
- `ssm:GetParameter`
- `ssm:DescribeParameters`

**CloudFormation**:
- `cloudformation:*`

**Lambda**:
- `lambda:CreateFunction`
- `lambda:UpdateFunctionCode`
- `lambda:UpdateFunctionConfiguration`

**API Gateway**:
- `apigateway:*`

**DynamoDB**:
- `dynamodb:CreateTable`
- `dynamodb:DescribeTable`

**IAM**:
- `iam:CreateRole`
- `iam:AttachRolePolicy`
- `iam:PassRole`

---

## Rollback

If deployment fails:

```bash
sam delete --stack-name cloudformation-stack-2025-aws-hackathon-bijak-mengeluh \
  --profile bijak-mengeluh-aws-iam \
  --region ap-southeast-2
```

Then redeploy after fixing issues.
