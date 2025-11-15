#!/bin/bash
set -e

# Configuration - override with environment variables
PROFILE="${AWS_PROFILE:-bijak-mengeluh-aws-iam}"
REGION="${AWS_REGION:-ap-southeast-2}"

echo "=== Bijak Mengeluh - API Keys Setup ==="
echo ""

# Prompt for Pinecone API key
read -p "Enter Pinecone API Key: " PINECONE_KEY
if [ -z "$PINECONE_KEY" ]; then
  echo "Error: Pinecone API key cannot be empty"
  exit 1
fi

# Prompt for Serper API key
read -p "Enter Serper API Key: " SERPER_KEY
if [ -z "$SERPER_KEY" ]; then
  echo "Error: Serper API key cannot be empty"
  exit 1
fi

echo ""
echo "Storing keys in AWS Systems Manager Parameter Store..."

# Store Pinecone key
aws ssm put-parameter \
  --name /bijak-mengeluh/pinecone-api-key \
  --value "$PINECONE_KEY" \
  --type SecureString \
  --description "Pinecone API key for Bijak Mengeluh project" \
  --overwrite \
  --profile "$PROFILE" \
  --region "$REGION"

echo "✓ Pinecone API key stored"

# Store Serper key
aws ssm put-parameter \
  --name /bijak-mengeluh/serper-api-key \
  --value "$SERPER_KEY" \
  --type SecureString \
  --description "Serper API key for Bijak Mengeluh project" \
  --overwrite \
  --profile "$PROFILE" \
  --region "$REGION"

echo "✓ Serper API key stored"
echo ""
echo "Setup complete! Keys are securely stored in AWS Parameter Store."
echo "You can now deploy using: ./scripts/deploy.sh"
