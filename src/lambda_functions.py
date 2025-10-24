import time
import boto3
import json
import os
import logging
from typing import List, Dict, Any, Optional

from botocore.config import Config
from pinecone import Pinecone

# ======================================================================================
# Logging Configuration
# ======================================================================================
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ======================================================================================
# Environment Variable Configuration
# ======================================================================================
PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
PINECONE_INDEX_NAME = os.environ["PINECONE_INDEX_NAME"]
CACHE_TABLE_NAME = os.environ["CACHE_TABLE_NAME"]
FINDER_FUNCTION_NAME = os.environ["FINDER_FUNCTION_NAME"]
AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-2")
BEDROCK_EMBED_MODEL_ID = os.environ.get("BEDROCK_EMBED_MODEL_ID", "cohere.embed-multilingual-v3")
BEDROCK_GENERATE_MODEL_ID = os.environ.get("BEDROCK_GENERATE_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")

# ======================================================================================
# AWS and Pinecone Client Initialization
# ======================================================================================
RETRY_CONFIG = Config(retries={'max_attempts': 5, 'mode': 'adaptive'})

bedrock_runtime = boto3.client(service_name='bedrock-runtime', region_name=AWS_REGION, config=RETRY_CONFIG)
lambda_client = boto3.client('lambda', region_name=AWS_REGION, config=RETRY_CONFIG)
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION, config=RETRY_CONFIG)
cache_table = dynamodb.Table(CACHE_TABLE_NAME)

pc = Pinecone(api_key=PINECONE_API_KEY)
pinecone_index = pc.Index(PINECONE_INDEX_NAME)

# ======================================================================================
# Prompt Templates
# ======================================================================================
COMPLAINT_GENERATION_PROMPT = """Human: Based on the following user complaint, please write a clear, polite, and detailed formal complaint suitable for submission to a government agency in Indonesia. The user's input is: '{user_prompt}'

Assistant:"""

RATIONALE_GENERATION_PROMPT = """Human: Here is a user's complaint:
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

# ======================================================================================
# Bedrock Model Interaction
# ======================================================================================
def _invoke_bedrock_model(model_id: str, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Invokes a Bedrock model and returns the parsed JSON response body.
    """
    logger.info(f"Invoking Bedrock model: {model_id}")
    try:
        response = bedrock_runtime.invoke_model(
            body=json.dumps(body),
            modelId=model_id,
            accept='application/json',
            contentType='application/json'
        )
        response_body = json.loads(response.get('body').read())
        logger.info("Successfully received and parsed response from model.")
        return response_body
    except Exception as e:
        logger.error(f"Error invoking Bedrock model {model_id}: {e}", exc_info=True)
        return {}

def get_embedding(text: str) -> List[float]:
    """
    Generates an embedding for the given text using a Bedrock embedding model.
    """
    logger.info(f"Getting embedding for text: '{text[:50]}...'")
    body = {"texts": [text], "input_type": "search_query"}
    response_body = _invoke_bedrock_model(BEDROCK_EMBED_MODEL_ID, body)
    return response_body.get('embeddings', [[]])[0]

def generate_complaint_text(user_prompt: str) -> str:
    """
    Generates a formal complaint text from a user's prompt.
    """
    logger.info("Generating formal complaint text.")
    prompt = COMPLAINT_GENERATION_PROMPT.format(user_prompt=user_prompt)
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}]
    }
    response_body = _invoke_bedrock_model(BEDROCK_GENERATE_MODEL_ID, body)
    if response_body and 'content' in response_body and response_body['content']:
        return response_body['content'][0].get('text', '').strip()
    return ""

def generate_rationale(user_prompt: str, ministry_metadata: Dict[str, str]) -> str:
    """
    Generates a rationale for suggesting a specific ministry.
    """
    logger.info(f"Generating rationale for ministry: {ministry_metadata.get('name')}")
    prompt = RATIONALE_GENERATION_PROMPT.format(
        user_prompt=user_prompt,
        ministry_name=ministry_metadata.get('name', 'N/A'),
        ministry_desc=ministry_metadata.get('text_content', 'No description available.')
    )
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "messages": [{"role": "user", "content": prompt}]
    }
    response_body = _invoke_bedrock_model(BEDROCK_GENERATE_MODEL_ID, body)
    if response_body and 'content' in response_body and response_body['content']:
        return response_body['content'][0].get('text', '').strip()
    return ""

# ======================================================================================
# Social Handle Retrieval Logic
# ======================================================================================
def _get_cached_social_handle(ministry_name: str) -> Optional[Dict[str, str]]:
    """Checks DynamoDB cache for a ministry's social handle."""
    try:
        logger.info(f"Checking cache for '{ministry_name}' social handle.")
        response = cache_table.get_item(Key={'ministry_name': ministry_name})
        if 'Item' in response:
            logger.info(f"CACHE HIT for '{ministry_name}'.")
            return response['Item']
    except Exception as e:
        logger.warning(f"Error reading from DynamoDB cache: {e}")
    logger.info(f"CACHE MISS for '{ministry_name}'.")
    return None

def _find_social_handle_via_lambda(ministry_name: str) -> Dict[str, str]:
    """Invokes a Lambda function to find a social handle."""
    logger.info(f"Invoking finder Lambda for '{ministry_name}'.")
    try:
        payload = json.dumps({"ministry_name": ministry_name})
        response = lambda_client.invoke(
            FunctionName=FINDER_FUNCTION_NAME,
            InvocationType='RequestResponse',
            Payload=payload
        )
        response_payload = json.loads(response['Payload'].read().decode('utf-8'))
        body = json.loads(response_payload.get('body', '{}'))
        logger.info(f"Finder Lambda returned: {body}")
        return {
            "handle": body.get('handle', 'NOT_FOUND'),
            "confidence": body.get('confidence', 'none')
        }
    except Exception as e:
        logger.error(f"Error invoking finder Lambda: {e}", exc_info=True)
        return {"handle": "NOT_FOUND", "status": "error"}

def _cache_social_handle(ministry_name: str, handle: str):
    """Caches a verified social handle in DynamoDB."""
    logger.info(f"Caching high-confidence handle for '{ministry_name}'.")
    try:
        cache_table.put_item(
            Item={
                'ministry_name': ministry_name,
                'handle': handle,
                'status': 'verified',
                'cached_at': int(time.time())
            }
        )
    except Exception as e:
        logger.error(f"Error writing to DynamoDB cache: {e}")

def get_social_handle(ministry_name: str) -> Dict[str, str]:
    """
    Retrieves a ministry's social media handle.
    This function implements a cache-aside pattern:
    1. Check DynamoDB cache.
    2. If miss, invoke a finder Lambda function.
    3. If the finder returns a high-confidence result, cache it.
    """
    cached_item = _get_cached_social_handle(ministry_name)
    if cached_item:
        return {"handle": cached_item['handle'], "status": cached_item['status']}

    finder_result = _find_social_handle_via_lambda(ministry_name)
    handle = finder_result.get('handle')
    confidence = finder_result.get('confidence')

    if handle and handle != 'NOT_FOUND' and confidence in ['high', 'medium']:
        status = 'verified' if confidence == 'high' else 'unverified'
        if status == 'verified':
            _cache_social_handle(ministry_name, handle)
        return {"handle": handle, "status": status}

    return {"handle": "NOT_FOUND", "status": finder_result.get("status", "none")}

# ======================================================================================
# Main Complaint Processing Logic
# ======================================================================================
def process_complaint(user_prompt: str) -> Dict[str, Any]:
    """
    Main business logic to process a user complaint.
    1. Creates an embedding from the user's prompt.
    2. Queries Pinecone to find relevant government bodies.
    3. Generates a formal complaint text.
    4. Generates a rationale for the top-suggested ministry.
    5. Retrieves the social media handle for the top ministry.
    """
    query_embedding = get_embedding(user_prompt)
    if not query_embedding:
        return {"error": "Could not generate embedding for the prompt."}

    query_response = pinecone_index.query(vector=query_embedding, top_k=3, include_metadata=True)
    suggested_contacts = [
        {
            "name": match['metadata']['name'],
            "score": match['score'],
            "description": match['metadata'].get('text_content', '')
        }
        for match in query_response.get('matches', [])
    ]
    logger.info(f"Suggested contacts: {[c['name'] for c in suggested_contacts]}")

    generated_text = generate_complaint_text(user_prompt)

    rationale = ""
    social_handle_info = {"handle": "NOT_FOUND", "status": "none"}
    if suggested_contacts:
        top_match = suggested_contacts[0]
        rationale = generate_rationale(user_prompt, {
            "name": top_match['name'],
            "text_content": top_match['description']
        })
        social_handle_info = get_social_handle(top_match['name'])

    return {
        'generated_text': generated_text,
        'suggested_contacts': suggested_contacts,
        'rationale': rationale,
        'social_handle_info': social_handle_info
    }

# ======================================================================================
# Lambda Handler
# ======================================================================================
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda entry point.
    """
    log_prefix = "LAMBDA_HANDLER"
    logger.info(f"{log_prefix}: Received event.")

    try:
        body = json.loads(event.get('body', '{}'))
        user_prompt = body.get('prompt')

        if not user_prompt:
            logger.warning(f"{log_prefix}: 'prompt' is missing from the request body.")
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Prompt is missing'})
            }

        start_time = time.time()
        result = process_complaint(user_prompt)
        end_time = time.time()
        logger.info(f"{log_prefix}: Total processing time: {end_time - start_time:.2f} seconds.")

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps(result)
        }

    except json.JSONDecodeError:
        logger.error(f"{log_prefix}: Invalid JSON in request body.")
        return {
            'statusCode': 400,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Invalid JSON format in request body'})
        }
    except Exception as e:
        logger.error(f"{log_prefix}: An unexpected error occurred: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Internal server error'})
        }
