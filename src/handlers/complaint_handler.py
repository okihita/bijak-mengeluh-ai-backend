import json
import time
import logging
from typing import Dict, Any

from services import BedrockService, PineconeService, SocialLookupService

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize services (reused across warm Lambda invocations)
bedrock_service = BedrockService()
pinecone_service = PineconeService()
social_lookup_service = SocialLookupService()

def process_complaint(user_prompt: str) -> Dict[str, Any]:
    """
    Main business logic to process a user complaint.
    1. Generate embedding from user prompt
    2. Find relevant ministries via Pinecone
    3. Generate formal complaint text
    4. Generate rationale for top ministry
    5. Retrieve social media handle
    """
    # Generate embedding
    query_embedding = bedrock_service.get_embedding(user_prompt)
    if not query_embedding:
        return {"error": "Could not generate embedding for the prompt"}
    
    # Find relevant ministries
    suggested_contacts = pinecone_service.find_relevant_ministries(query_embedding, top_k=3)
    
    # Generate formal complaint text
    generated_text = bedrock_service.generate_complaint_text(user_prompt)
    
    # Generate rationale and get social handle for top ministry
    rationale = ""
    social_handle_info = {"handle": "NOT_FOUND", "status": "none"}
    
    if suggested_contacts:
        top_match = suggested_contacts[0]
        rationale = bedrock_service.generate_rationale(
            user_prompt,
            top_match['name'],
            top_match['description']
        )
        social_handle_info = social_lookup_service.get_social_handle(top_match['name'])
    
    return {
        'generated_text': generated_text,
        'suggested_contacts': suggested_contacts,
        'rationale': rationale,
        'social_handle_info': social_handle_info
    }

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda entry point."""
    logger.info("Received complaint generation request")
    
    try:
        body = json.loads(event.get('body', '{}'))
        user_prompt = body.get('prompt')
        
        if not user_prompt:
            logger.warning("'prompt' is missing from request body")
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Prompt is missing'})
            }
        
        start_time = time.time()
        result = process_complaint(user_prompt)
        elapsed_time = time.time() - start_time
        
        logger.info(f"Processing completed in {elapsed_time:.2f} seconds")
        
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
        logger.error("Invalid JSON in request body")
        return {
            'statusCode': 400,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Invalid JSON format in request body'})
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Internal server error'})
        }
