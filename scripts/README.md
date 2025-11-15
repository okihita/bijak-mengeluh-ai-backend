# Scripts

Reproducible scripts for deployment and data collection.

---

## Configuration

All scripts use environment variables for configuration:

```bash
# AWS Configuration
export AWS_PROFILE="your-aws-profile"        # Default: bijak-mengeluh-aws-iam
export AWS_REGION="your-aws-region"          # Default: ap-southeast-2

# API Keys
export SERPER_API_KEY="your-serper-key"      # Required for scraping

# DynamoDB
export AGENCIES_TABLE_NAME="your-table"      # Default: agencies
```

---

## Deployment Scripts

### setup-secrets.sh
Store API keys in AWS Systems Manager Parameter Store.

```bash
./setup-secrets.sh
```

**Prompts for:**
- Pinecone API key
- Serper API key

**Stores in:** `/bijak-mengeluh/pinecone-api-key` and `/bijak-mengeluh/serper-api-key`

### deploy.sh
Build and deploy the Lambda functions.

```bash
./deploy.sh
```

**Steps:**
1. Retrieves API keys from Parameter Store
2. Builds SAM application
3. Deploys to AWS

---

## Data Collection Scripts

### 1. create_agencies_table.py
Create DynamoDB table for agency data.

```bash
python create_agencies_table.py
```

**Creates:**
- Table: `agencies` (or `$AGENCIES_TABLE_NAME`)
- Primary key: `agency_id`
- GSI: `keyword-index`
- Billing: PAY_PER_REQUEST

### 2. scrape_dki_agencies.py
Scrape DKI Jakarta provincial and city agencies.

```bash
export SERPER_API_KEY="your-key"
python scrape_dki_agencies.py
```

**Scrapes:**
- 15 provincial dinas (DKI Jakarta level)
- 75 city dinas (5 cities × 15 dinas each)
- **Total:** 90 agencies

**Output:**
- Stores in DynamoDB table
- Saves to `dki_agencies.json`

**Time:** ~45 minutes  
**Cost:** ~$0.03

### 3. scrape_national_ministries.py
Scrape 34 national ministries.

```bash
export SERPER_API_KEY="your-key"
python scrape_national_ministries.py
```

**Scrapes:**
- 34 national ministries
- Includes keywords for matching

**Output:**
- Stores in DynamoDB table
- Saves to `national_ministries.json`

**Time:** ~20 minutes  
**Cost:** ~$0.02

---

## Prerequisites

### AWS CLI
```bash
aws configure --profile your-profile
# Region: ap-southeast-2 (or your preferred region)
```

### SAM CLI
```bash
# macOS
brew install aws-sam-cli

# Linux
pip install aws-sam-cli
```

### Python Dependencies
```bash
pip install boto3 requests
```

### Serper API Key
1. Visit https://serper.dev
2. Sign up (free tier: 2,500 queries/month)
3. Copy API key

---

## Usage Examples

### Deploy to Different Region
```bash
export AWS_REGION="us-east-1"
./deploy.sh
```

### Use Different AWS Profile
```bash
export AWS_PROFILE="my-profile"
./setup-secrets.sh
./deploy.sh
```

### Use Custom Table Name
```bash
export AGENCIES_TABLE_NAME="my-agencies"
python create_agencies_table.py
python scrape_dki_agencies.py
```

---

## Troubleshooting

### Error: SERPER_API_KEY not set
```bash
export SERPER_API_KEY="your-key"
```

### Error: Table already exists
```bash
aws dynamodb delete-table \
  --table-name agencies \
  --region ap-southeast-2
# Wait 30 seconds
python create_agencies_table.py
```

### Error: AWS credentials not found
```bash
aws configure --profile your-profile
```

### Error: SAM build failed
```bash
# Ensure Python 3.12 is installed
python3 --version

# Clean and rebuild
rm -rf .aws-sam
sam build
```

---

## Cost Breakdown

| Component | Cost |
|-----------|------|
| Serper API | $0 (free tier) |
| Bedrock LLM | $0.04 |
| DynamoDB | $0.01 |
| Lambda | $0 (free tier) |
| **Total** | **$0.05** |

---

## Files Generated

- `dki_agencies.json` - DKI Jakarta agencies
- `national_ministries.json` - National ministries

**Note:** These files are for reference only. Production uses DynamoDB.

---

## Security Notes

- Never commit API keys to git
- Use environment variables or Parameter Store
- Rotate API keys regularly
- Use least-privilege IAM roles
