# Setup Instructions

## API Keys Configuration

This project uses AWS Systems Manager Parameter Store to securely store API keys.

### First-Time Setup

Run the setup script to store your API keys:

```bash
./scripts/setup-secrets.sh
```

Or manually store them:

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

### Viewing Stored Keys

```bash
# View Pinecone key
aws ssm get-parameter \
  --name /bijak-mengeluh/pinecone-api-key \
  --with-decryption \
  --query Parameter.Value \
  --output text \
  --profile bijak-mengeluh-aws-iam \
  --region ap-southeast-2

# View Serper key
aws ssm get-parameter \
  --name /bijak-mengeluh/serper-api-key \
  --with-decryption \
  --query Parameter.Value \
  --output text \
  --profile bijak-mengeluh-aws-iam \
  --region ap-southeast-2
```

### Updating Keys

```bash
# Add --overwrite flag to update existing keys
aws ssm put-parameter \
  --name /bijak-mengeluh/pinecone-api-key \
  --value "NEW_KEY" \
  --type SecureString \
  --overwrite \
  --profile bijak-mengeluh-aws-iam \
  --region ap-southeast-2
```

### Deployment

The deployment script automatically retrieves keys from Parameter Store:

```bash
./scripts/deploy.sh
```

Or manually:

```bash
sam deploy \
  --profile bijak-mengeluh-aws-iam \
  --parameter-overrides \
    PineconeApiKey=$(aws ssm get-parameter --name /bijak-mengeluh/pinecone-api-key --with-decryption --query Parameter.Value --output text --profile bijak-mengeluh-aws-iam --region ap-southeast-2) \
    SerperApiKey=$(aws ssm get-parameter --name /bijak-mengeluh/serper-api-key --with-decryption --query Parameter.Value --output text --profile bijak-mengeluh-aws-iam --region ap-southeast-2)
```

## Required IAM Permissions

Your IAM user needs these permissions:
- `ssm:PutParameter`
- `ssm:GetParameter`
- `ssm:DescribeParameters`

Add this policy to your IAM user if missing.
