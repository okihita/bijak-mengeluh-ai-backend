import boto3
import json
import os
from pinecone import Pinecone

import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# --- Initialization ---
# Load environment variables set in the Lambda console
PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
PINECONE_INDEX_NAME = os.environ["PINECONE_INDEX_NAME"]
AWS_REGION = "ap-southeast-2"

# Initialize clients ONCE outside the handler
bedrock_runtime = boto3.client(service_name='bedrock-runtime', region_name=AWS_REGION)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

BEDROCK_EMBED_MODEL_ID = "cohere.embed-multilingual-v3"
BEDROCK_GENERATE_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"

def get_embedding(text):
    """Generates an embedding for the user's query."""
    body = json.dumps({"texts": [text], "input_type": "search_query"})

    logger.info(f"Starting getting embedding from model {BEDROCK_EMBED_MODEL_ID}")

    response = bedrock_runtime.invoke_model(
        body=body,
        modelId=BEDROCK_EMBED_MODEL_ID,
        accept='application/json',
        contentType='application/json'
    )
    response_body = json.loads(response.get('body').read())
    return response_body['embeddings'][0]

def generate_complaint_text(user_prompt):
    """Generates the complaint text using Claude (same as Day 1)."""
    prompt = f"Human: Based on the following user complaint, please write a clear, polite, and detailed formal complaint suitable for submission to a government agency in Indonesia. The user's input is: '{user_prompt}'\n\nAssistant:"

    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}]
    }

    logger.info(f"Starting generating complaint text from model {BEDROCK_GENERATE_MODEL_ID}")

    response = bedrock_runtime.invoke_model(
        body=json.dumps(request_body),
        modelId=BEDROCK_GENERATE_MODEL_ID,
        accept='application/json',
        contentType='application/json'
    )
    response_body = json.loads(response.get('body').read())
    return response_body['content'][0]['text']

def lambda_handler(event, context):

    logger.info(f"Request Origin: {event}")

    try:
        body = json.loads(event.get('body', '{}'))
        user_prompt = body.get('prompt')

        if not user_prompt:
            return {'statusCode': 400, 'headers': {'Access-Control-Allow-Origin': '*'}, 'body': json.dumps({'error': 'Prompt is missing'})}

        # --- TASK 1: Generate Complaint Text (Parallelizable) ---
        generated_text = generate_complaint_text(user_prompt)

        # --- TASK 2: Get Embedding for User Prompt ---
        query_embedding = get_embedding(user_prompt)

        # --- TASK 3: Query Pinecone ---
        query_response = index.query(
            vector=query_embedding,
            top_k=3, # Get the top 3 most relevant ministries
            include_metadata=True
        )

        suggested_contacts = []
        for match in query_response.get('matches', []):
            suggested_contacts.append({
                "name": match['metadata']['name'],
                "score": match['score']
            })

        # --- TASK 4: Return Both Results ---
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({
                'generated_text': generated_text,
                'suggested_contacts': suggested_contacts
            })
        }

    except Exception as e:
        logger.info(f"Error: {e}")

        return {'statusCode': 500, 'headers': {'Access-Control-Allow-Origin': '*'}, 'body': json.dumps({'error': 'Internal server error'})}