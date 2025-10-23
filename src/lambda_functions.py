import time
import boto3
import json
import os
from pinecone import Pinecone

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

from botocore.config import Config

# --- CONFIGURATION ---

PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
PINECONE_INDEX_NAME = os.environ["PINECONE_INDEX_NAME"]
AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-2")
BEDROCK_EMBED_MODEL_ID = os.environ.get("BEDROCK_EMBED_MODEL_ID", "cohere.embed-multilingual-v3")
BEDROCK_GENERATE_MODEL_ID = os.environ.get("BEDROCK_GENERATE_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")

# Configure retries
# Use adaptive retry mode, which is designed to be more intelligent
# about backing off when it detects throttling.
retry_config = Config(
    retries={'max_attempts': 5, 'mode': 'adaptive'}
)

# Initialize clients
bedrock_runtime = boto3.client(service_name='bedrock-runtime', region_name=AWS_REGION, config=retry_config)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

# --- CONFIGURATION ---
def _invoke_bedrock_model(model_id, body):
    """Helper function to invoke a Bedrock model and parse the response."""
    logger.info(f"Invoking Bedrock model: {model_id}")
    response = bedrock_runtime.invoke_model(
        body=body,
        modelId=model_id,
        accept='application/json',
        contentType='application/json'
    )
    response_body = json.loads(response.get('body').read())
    logger.info("Successfully received and parsed response from model.")
    return response_body

def get_embedding(text):
    logger.info(f"Getting embedding for text: {text}")
    body = json.dumps({"texts": [text], "input_type": "search_query"})
    response_body = _invoke_bedrock_model(BEDROCK_EMBED_MODEL_ID, body)
    return response_body['embeddings'][0]

def generate_complaint_text(user_prompt):
    logger.info(f"Generating complaint text for user prompt: {user_prompt}")
    prompt = f"Human: Based on the following user complaint, please write a clear, polite, and detailed formal complaint suitable for submission to a government agency in Indonesia. The user's input is: '{user_prompt}'\n\nAssistant:"
    
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}]
    }
    response_body = _invoke_bedrock_model(BEDROCK_GENERATE_MODEL_ID, json.dumps(request_body))
    return response_body['content'][0]['text']

def generate_rationale(user_prompt, ministry_metadata):
    logger.info(f"Generating rationale for user prompt: {user_prompt} versus ministry: {ministry_metadata}")
    ministry_name = ministry_metadata.get('name', 'N/A')
    ministry_desc = ministry_metadata.get('text_content', 'No description available.')

    prompt = f"""Human: Here is a user's complaint:
<complaint>
{user_prompt}
</complaint>

And here is the top-matched government ministry and its function:
<ministry>
Nama: {ministry_name}
Fungsi: {ministry_desc}
</ministry>

Your task is to write a brief, clear rationale (in 1-2 sentences) explaining *why* this ministry is the correct one to handle this specific complaint. 
Directly connect key phrases from the complaint to the ministry's function.
Example: "Kementerian PUPR disarankan karena keluhan Anda tentang 'jalan rusak' dan 'jembatan' terkait langsung dengan tanggung jawab mereka atas 'infrastruktur jalan' dan 'jembatan'."

Write only the rationale.

Assistant:"""
    
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "messages": [{"role": "user", "content": prompt}]
    }

    response_body = _invoke_bedrock_model(BEDROCK_GENERATE_MODEL_ID, json.dumps(request_body))
    return response_body['content'][0]['text']

def process_complaint(user_prompt):
    """Main business logic to process the user complaint."""
    query_embedding = get_embedding(user_prompt)

    query_response = index.query(vector=query_embedding, top_k=3, include_metadata=True)
    
    suggested_contacts = [
        {"name": match['metadata']['name'], "score": match['score'], "description": match['metadata'].get('text_content', '')}
        for match in query_response.get('matches', [])
    ]
    logger.info(f"Suggested contacts: {suggested_contacts}")

    generated_text = generate_complaint_text(user_prompt)

    rationale = ""
    if suggested_contacts:
        top_match_metadata = {
            "name": suggested_contacts[0]['name'],
            "text_content": suggested_contacts[0]['description']
        }
        rationale = generate_rationale(user_prompt, top_match_metadata)
    logger.info(f"Rationale: {rationale}")

    return {
        'generated_text': generated_text,
        'suggested_contacts': suggested_contacts,
        'rationale': rationale
    }

def lambda_handler(event, context):
    logger.info(f"Received event: {event}")
    try:
        body = json.loads(event.get('body', '{}'))
        user_prompt = body.get('prompt')

        if not user_prompt:
            logger.warning("Request received without a 'prompt' in the body.")
            return {'statusCode': 400, 'headers': {'Access-Control-Allow-Origin': '*'}, 'body': json.dumps({'error': 'Prompt is missing'})}
        
        result = process_complaint(user_prompt)

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps(result)
        }

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        return {'statusCode': 500, 'headers': {'Access-Control-Allow-Origin': '*'}, 'body': json.dumps({'error': 'Internal server error'})}