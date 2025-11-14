import os

# AWS Configuration
AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-2")

# Pinecone Configuration
PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
PINECONE_INDEX_NAME = os.environ["PINECONE_INDEX_NAME"]

# DynamoDB Configuration
CACHE_TABLE_NAME = os.environ["CACHE_TABLE_NAME"]

# Lambda Configuration
FINDER_FUNCTION_NAME = os.environ["FINDER_FUNCTION_NAME"]

# Bedrock Model Configuration
BEDROCK_EMBED_MODEL_ID = os.environ.get("BEDROCK_EMBED_MODEL_ID", "cohere.embed-multilingual-v3")
BEDROCK_GENERATE_MODEL_ID = os.environ.get("BEDROCK_GENERATE_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")

# Serper Configuration
SERPER_API_KEY = os.environ.get("SERPER_API_KEY", "")
