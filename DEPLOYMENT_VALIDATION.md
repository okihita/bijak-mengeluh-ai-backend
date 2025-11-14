# Deployment Validation Report

## Template Resources (From Scratch Deployment)

### Parameters Required
1. `PineconeApiKey` - API key for Pinecone vector database
2. `PineconeIndexName` - Name of Pinecone index (default: 2025-aws-hackathon)
3. `SerperApiKey` - API key for Serper.dev search
4. `CacheTableName` - DynamoDB table name (default: BijakMengeluhSocialsCacheTable)
5. `BrandedApiDomainName` - Custom domain (default: brain.bijakmengeluh.id)
6. `BrandedApiDomainCertificateArn` - ACM certificate ARN

### Resources Created

#### 1. DynamoDB Table
- **Resource**: `BijakMengeluhCacheTable`
- **Type**: AWS::DynamoDB::Table
- **Purpose**: Caches verified social media handles
- **Billing**: PAY_PER_REQUEST (serverless)

#### 2. HTTP API Gateway
- **Resource**: `ComplaintGenerationHttpApi`
- **Type**: AWS::Serverless::HttpApi
- **Features**:
  - CORS enabled for localhost:3000 and bijakmengeluh.id
  - Custom domain with SSL certificate
  - Regional endpoint

#### 3. Main Lambda Function
- **Resource**: `BijakMengeluhComplaintGenerationFunction`
- **Type**: AWS::Serverless::Function
- **Runtime**: Python 3.12
- **Memory**: 512 MB
- **Timeout**: 60 seconds
- **Handler**: lambda_functions.lambda_handler
- **Permissions**:
  - AmazonBedrockFullAccess
  - DynamoDB CRUD on cache table
  - Invoke BijakMengeluhSocialFinderFunction
- **Trigger**: POST /generate

#### 4. Finder Lambda Function
- **Resource**: `BijakMengeluhSocialFinderFunction`
- **Type**: AWS::Serverless::Function
- **Runtime**: Python 3.12
- **Memory**: 512 MB
- **Timeout**: 30 seconds
- **Handler**: social_finder.lambda_handler
- **Permissions**:
  - AmazonBedrockFullAccess

### Auto-Generated Resources (by SAM)
SAM will automatically create:
- IAM Roles for both Lambda functions
- Lambda permissions for API Gateway
- CloudWatch Log Groups
- API Gateway stages and deployments
- Custom domain mapping (if domain exists)

## Validation Status

✅ **Template is valid** (sam validate passed)
✅ **All required resources defined**
✅ **IAM permissions properly scoped**
✅ **Environment variables configured**
✅ **CORS properly configured**

## Prerequisites for Clean Deployment

### Required in AWS Account
1. ✅ ACM Certificate (already exists: arn:aws:acm:ap-southeast-2:986517526233:certificate/ccf38539-1caa-4ae9-8f86-70ab1b4408c0)
2. ⚠️  Route53 hosted zone for bijakmengeluh.id (if using custom domain)
3. ✅ Bedrock model access enabled in ap-southeast-2
4. ✅ API keys stored in Parameter Store (via setup-secrets.sh)

### External Dependencies
1. ✅ Pinecone index created and populated with ministry embeddings
2. ✅ Serper.dev API key obtained

## Deployment Command (From Scratch)

```bash
# Build
sam build --profile bijak-mengeluh-aws-iam

# Deploy (will prompt for parameters)
sam deploy --profile bijak-mengeluh-aws-iam --guided

# Or deploy with stored config
sam deploy --profile bijak-mengeluh-aws-iam
```

## What Happens if Stack is Deleted

If the CloudFormation stack is completely deleted, running `sam deploy` will:

1. ✅ Create new DynamoDB table (data will be lost)
2. ✅ Create new API Gateway
3. ✅ Create new Lambda functions with fresh code
4. ✅ Create new IAM roles
5. ✅ Re-establish custom domain mapping
6. ⚠️  Require manual Route53 update if domain mapping changes

## Potential Issues

1. **Custom Domain**: If the domain is already mapped to another API, deployment will fail
2. **Certificate**: Must exist in the same region (ap-southeast-2)
3. **Pinecone Index**: Must exist before deployment (not created by template)
4. **API Keys**: Must be provided as parameters during deployment

## Conclusion

✅ **The template is complete and will create all necessary resources from scratch**
✅ **No missing dependencies in the template itself**
⚠️  **External services (Pinecone, Serper, ACM cert) must exist beforehand**
