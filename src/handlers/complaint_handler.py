import json
import time
import logging
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor

from services import BedrockService, PineconeService, SocialLookupService

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize services (reused across warm Lambda invocations)
bedrock_service = BedrockService()
pinecone_service = PineconeService()
social_lookup_service = SocialLookupService()

def process_complaint(user_prompt: str, tone: str = "formal") -> Dict[str, Any]:
    """
    Main business logic to process a user complaint with parallel execution.
    1. Generate embedding from user prompt
    2. Find relevant ministries via Pinecone
    3. Generate formal complaint text (parallel with step 2)
    4. Generate rationale for top ministry (parallel with social lookup)
    5. Retrieve social media handle
    
    Args:
        user_prompt: The user's complaint text
        tone: The tone of the complaint (formal, funny, angry)
    """
    # Step 1: Generate embedding (required for next steps)
    query_embedding = bedrock_service.get_embedding(user_prompt)
    if not query_embedding:
        return {"error": "Tidak bisa membuat embedding. Coba lagi ya."}
    
    # Step 2 & 3: Run ministry search and text generation in parallel
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_contacts = executor.submit(
            pinecone_service.find_relevant_ministries, query_embedding, 3
        )
        future_text = executor.submit(
            bedrock_service.generate_complaint_text, user_prompt, tone
        )
        
        suggested_contacts = future_contacts.result()
        generated_text = future_text.result()
    
    # Step 4 & 5: Generate rationale and get social handle in parallel
    rationale = ""
    social_handle_info = {"handle": "NOT_FOUND", "status": "none"}
    
    if suggested_contacts:
        top_match = suggested_contacts[0]
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_rationale = executor.submit(
                bedrock_service.generate_rationale,
                user_prompt,
                top_match['name'],
                top_match['description']
            )
            future_social = executor.submit(
                social_lookup_service.get_social_handle,
                top_match['name']
            )
            
            rationale = future_rationale.result()
            social_handle_info = future_social.result()
    
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
        # Support both 'complaint' (new) and 'prompt' (legacy) for backward compatibility
        user_complaint = body.get('complaint') or body.get('prompt')
        tone = body.get('tone', 'formal')  # Default to formal if not provided
        
        if not user_complaint:
            logger.warning("'complaint' is missing from request body")
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Keluhan belum diisi. Tulis dulu keluhannya ya.'})
            }
        
        if len(user_complaint.strip()) < 20:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Keluhan terlalu pendek. Minimal 20 karakter ya.'})
            }
        
        start_time = time.time()
        result = process_complaint(user_complaint, tone)
        elapsed_time = time.time() - start_time
        
        logger.info(f"Processing completed in {elapsed_time:.2f} seconds")
        
        # Check if there was an error in processing
        if 'error' in result:
            return {
                'statusCode': 500,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps(result)
            }
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST',
                'X-Processing-Time': f'{elapsed_time:.2f}s'
            },
            'body': json.dumps(result)
        }
    
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return {
            'statusCode': 400,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Format data salah. Coba lagi ya.'})
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Ada masalah di server. Coba lagi dalam beberapa saat.'})
        }
