import boto3
import json
import re
import requests
import logging
from typing import Dict, Any, Optional

from config import settings

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize clients
bedrock_runtime = boto3.client(service_name='bedrock-runtime', region_name=settings.AWS_REGION)
requests_session = requests.Session()

# Prompt template
HANDLE_EXTRACTION_PROMPT = """Human: I have performed a web search for the official X/Twitter handle for "{ministry_name}".
Your task is to analyze the following search result snippets and extract *only* the official, verified X/Twitter handle (which must start with '@').

<search_results>
{search_results}
</search_results>

Guidelines:
1.  Analyze the snippets for official handles (starting with '@').
2.  Prioritize handles from `twitter.com` or `x.com` links or official-sounding titles.
3.  Assess your confidence:
    - "high": You are very certain. The handle is clearly stated (e.g., "Official X: @KemenPU").
    - "medium": A handle is mentioned, but it's not explicitly verified (e.g., in a news article snippet).
    - "low": A handle is present but seems unofficial or ambiguous.
    - "none": You cannot find any plausible handle.
4.  Respond with *only* a valid JSON object in this exact format:
    `{{"handle": "@handle_name", "confidence": "high"}}`
    or
    `{{"handle": "NOT_FOUND", "confidence": "none"}}`

JSON Response:
Assistant:"""

def call_serper_api(query: str) -> Optional[Dict[str, Any]]:
    """Performs a web search using the Serper API."""
    logger.info(f"Calling Serper API with query: '{query}'")
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': settings.SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests_session.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        logger.info("Serper API call successful")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Serper API call failed: {e}")
        return None

def extract_handle_with_bedrock(ministry_name: str, search_results_text: str) -> Dict[str, str]:
    """Uses Bedrock to extract Twitter handle from search results."""
    logger.info(f"Extracting handle for '{ministry_name}' using Bedrock")
    
    prompt = HANDLE_EXTRACTION_PROMPT.format(
        ministry_name=ministry_name,
        search_results=search_results_text
    )
    
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 256,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        response = bedrock_runtime.invoke_model(
            body=json.dumps(body),
            modelId=settings.BEDROCK_GENERATE_MODEL_ID,
            accept='application/json',
            contentType='application/json'
        )
        response_body = json.loads(response.get('body').read())
        
        if response_body and 'content' in response_body and response_body['content']:
            raw_text = response_body['content'][0].get('text', '').strip()
            logger.info(f"Bedrock raw response: {raw_text}")
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
                return {
                    "handle": result.get("handle", "NOT_FOUND"),
                    "confidence": result.get("confidence", "none")
                }
    except Exception as e:
        logger.error(f"Error extracting handle with Bedrock: {e}", exc_info=True)
    
    return {"handle": "NOT_FOUND", "confidence": "none"}

def find_social_handle(ministry_name: str) -> Dict[str, str]:
    """Main logic to find social media handle for a ministry."""
    logger.info(f"Finding social handle for: {ministry_name}")
    
    # Perform web search
    query = f"{ministry_name} official twitter X handle"
    search_results = call_serper_api(query)
    
    if not search_results:
        return {"handle": "NOT_FOUND", "confidence": "none"}
    
    # Format search results for Bedrock
    organic_results = search_results.get('organic', [])
    if not organic_results:
        logger.warning("No organic search results found")
        return {"handle": "NOT_FOUND", "confidence": "none"}
    
    search_results_text = "\n\n".join([
        f"Title: {result.get('title', 'N/A')}\nSnippet: {result.get('snippet', 'N/A')}\nLink: {result.get('link', 'N/A')}"
        for result in organic_results[:5]
    ])
    
    # Extract handle using Bedrock
    return extract_handle_with_bedrock(ministry_name, search_results_text)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda entry point for social finder."""
    logger.info("Social finder Lambda invoked")
    
    try:
        ministry_name = event.get('ministry_name')
        
        if not ministry_name:
            logger.warning("'ministry_name' is missing from event")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'ministry_name is required'})
            }
        
        result = find_social_handle(ministry_name)
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    
    except Exception as e:
        logger.error(f"Unexpected error in social finder: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
