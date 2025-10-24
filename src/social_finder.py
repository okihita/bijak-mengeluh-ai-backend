import boto3
import json
import os
import re
import requests
import logging
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError

# ======================================================================================
# Logging Configuration
# ======================================================================================
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ======================================================================================
# Configuration Constants
# ======================================================================================
SERPER_API_KEY = os.environ.get("SERPER_API_KEY")
AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-2")
BEDROCK_GENERATE_MODEL_ID = os.environ.get("BEDROCK_GENERATE_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
DEFAULT_MINISTRY_NAME_FAILSAFE = "Kementerian PUPR"  # Failsafe for simple tests or missing input

# ======================================================================================
# Pre-flight Checks
# ======================================================================================
if not SERPER_API_KEY:
    logger.error("SERPER_API_KEY environment variable not set. This is critical for web search.")
    # In a real-world scenario, you might want to raise an exception or exit here.

# ======================================================================================
# Client Initialization
# ======================================================================================
bedrock_runtime = boto3.client(service_name='bedrock-runtime', region_name=AWS_REGION)
requests_session = requests.Session() # Use a session for better performance with multiple requests

# ======================================================================================
# Prompt Templates
# ======================================================================================
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

# ======================================================================================
# Core Logic Functions
# ======================================================================================
def _call_serper_api(query: str) -> Optional[Dict[str, Any]]:
    """
    Performs a web search using the Serper API.

    Args:
        query: The search query string.

    Returns:
        A dictionary containing the JSON response from Serper API, or None if an error occurs.
    """
    logger.info(f"Calling Serper API with query: '{query}'")
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }

    try:
        response = requests_session.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error during Serper API call for query '{query}': {e}")
        return None

def _format_serper_results_for_ai(serper_response: Dict[str, Any]) -> str:
    """
    Formats the raw Serper API response into a string suitable for AI processing.

    Args:
        serper_response: The JSON response dictionary from the Serper API.

    Returns:
        A string containing formatted search result snippets.
    """
    if not serper_response or not serper_response.get('organic'):
        return "No relevant search results found."

    search_snippets = "\n".join(
        f"<result>\n<title>{item.get('title', '')}</title>\n<link>{item.get('link', '')}</link>\n<snippet>{item.get('snippet', '')}</snippet>\n</result>"
        for item in serper_response.get('organic', [])
    )
    logger.info(f"Formatted search results for AI: {search_snippets[:200]}...")
    return search_snippets

def _extract_handle_from_text_with_bedrock(formatted_search_results: str, ministry_name: str) -> Dict[str, str]:
    """
    Uses a Bedrock model (Claude) to extract the official social media handle from search results.

    Args:
        formatted_search_results: A string containing formatted search result snippets.
        ministry_name: The name of the ministry being searched for.

    Returns:
        A dictionary with 'handle' and 'confidence' keys.
    """
    logger.info(f"Extracting handle for '{ministry_name}' using Bedrock.")
    prompt = HANDLE_EXTRACTION_PROMPT.format(ministry_name=ministry_name, search_results=formatted_search_results)

    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 150,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = bedrock_runtime.invoke_model(
            body=json.dumps(request_body),
            modelId=BEDROCK_GENERATE_MODEL_ID,
            accept='application/json',
            contentType='application/json'
        )
        response_body = json.loads(response.get('body').read())

        ai_response_text = response_body.get('content', [{}])[0].get('text', '').strip()
        logger.info(f"Raw AI response text: {ai_response_text}")

        # Robustly find and parse the JSON object from the AI's response
        json_match = re.search(r'\{.*\}', ai_response_text, re.DOTALL)
        if not json_match:
            logger.warning(f"AI response did not contain a valid JSON object. Response: {ai_response_text}")
            return {"handle": "NOT_FOUND", "confidence": "none"}

        extracted_data = json.loads(json_match.group(0))
        logger.info(f"AI extracted data: {extracted_data}")
        return extracted_data

    except (ClientError, json.JSONDecodeError, ValueError, IndexError) as e:
        logger.error(f"Error during Bedrock invocation or AI response parsing: {e}", exc_info=True)
        return {"handle": "NOT_FOUND", "confidence": "none"}

# ======================================================================================
# Lambda Handler
# ======================================================================================
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda entry point for finding social media handles.

    Args:
        event: The Lambda event object, expected to contain 'ministry_name'.
        context: The Lambda context object.

    Returns:
        A dictionary representing the HTTP response, containing the extracted social handle
        and confidence level.
    """
    log_prefix = "LAMBDA_HANDLER"
    logger.info(f"{log_prefix}: Received event.")

    ministry_name = None
    try:
        # Handle both direct Lambda invocation (dict) and API Gateway proxy integration (JSON string in 'body')
        if 'body' in event and isinstance(event['body'], str):
            event_body = json.loads(event['body'])
        else:
            event_body = event
        ministry_name = event_body.get('ministry_name')
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"{log_prefix}: Error parsing event body: {e}. Raw event: {event}")

    if not ministry_name:
        logger.warning(f"{log_prefix}: 'ministry_name' not found in event. Using failsafe: {DEFAULT_MINISTRY_NAME_FAILSAFE}")
        ministry_name = DEFAULT_MINISTRY_NAME_FAILSAFE
        # For a production system, consider returning a 400 error here if ministry_name is strictly required.
        # return {'statusCode': 400, 'body': json.dumps({'error': 'ministry_name is required'})}

    # Perform web search
    search_query = f"official X (Twitter) handle for {ministry_name} Indonesia"
    serper_response = _call_serper_api(search_query)

    if not serper_response:
        logger.error(f"{log_prefix}: Failed to get search results for '{ministry_name}'.")
        return {'statusCode': 500, 'body': json.dumps({'error': 'Failed to perform web search'})}

    formatted_search_results = _format_serper_results_for_ai(serper_response)

    # Extract handle using AI
    extracted_data = _extract_handle_from_text_with_bedrock(formatted_search_results, ministry_name)

    # Prepare and return the final response
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(extracted_data)
    }
