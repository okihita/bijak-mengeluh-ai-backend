import boto3
import json
import os
import re
import requests
from botocore.exceptions import ClientError

# --- Initialization ---
SERPER_API_KEY = os.environ.get("SERPER_API_KEY")
AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-2")
BEDROCK_GENERATE_MODEL_ID = os.environ.get("BEDROCK_GENERATE_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
DEFAULT_MINISTRY_NAME_FAILSAFE = "Kementerian PUPR" # Failsafe for simple tests

# --- Pre-flight checks ---
if not SERPER_API_KEY:
    raise ValueError("SERPER_API_KEY environment variable not set.")

# --- Boto3 Client (reused across invocations) ---
bedrock_runtime = boto3.client(service_name='bedrock-runtime', region_name=AWS_REGION)

def perform_web_search(ministry_name):
    """
    Performs a targeted Google search using Serper API.
    """
    print(f"Performing search for: {ministry_name}")
    url = "https://google.serper.dev/search"
    
    # Precise query to find the official X/Twitter handle
    query = f"official X (Twitter) handle for {ministry_name} Indonesia"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes
        results = response.json()
        
        # Use a generator expression and join for efficiency and readability
        search_snippets = "\n".join(
            f"<result>\n<title>{item.get('title', '')}</title>\n<link>{item.get('link', '')}</link>\n<snippet>{item.get('snippet', '')}</snippet>\n</result>"
            for item in results.get('organic', [])
        )
            
        print(f"Search results: {search_snippets}")
        return search_snippets
        
    except requests.exceptions.RequestException as e:
        print(f"Error during Serper API call: {e}")
        return None

def extract_handle_with_ai(search_results, ministry_name):
    """
    Uses Bedrock (Claude) to read the search results and extract the official handle.
    """
    print("Extracting handle with AI...")
    
    # This is a powerful extraction prompti
    prompt = f"""Human: I have performed a web search for the official X/Twitter handle for "{ministry_name}".
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
        
        # The AI's response is a JSON string, so we need to parse it
        ai_response_text = response_body.get('content', [{}])[0].get('text', '').strip()
        
        # Use regex to robustly find the JSON object in the response text
        json_match = re.search(r'\{.*\}', ai_response_text, re.DOTALL)
        if not json_match:
            raise ValueError(f"AI response did not contain a valid JSON object. Response: {ai_response_text}")
        
        data = json.loads(json_match.group(0))
        
        print(f"AI extracted data: {data}")
        return data
        
    except (ClientError, json.JSONDecodeError, ValueError, IndexError) as e:
        print(f"Error during Bedrock extraction or JSON parsing: {e}")
        return {"handle": "NOT_FOUND", "confidence": "none"}

def lambda_handler(event, context):
    print(f"Received event: {event}")
    
    ministry_name = None
    try:
        # The event body from API Gateway is a string that needs to be parsed.
        # A direct Lambda invoke might pass the dict directly.
        event_body = json.loads(event.get('body', '{}')) if 'body' in event else event
        ministry_name = event_body.get('ministry_name')
    except (json.JSONDecodeError, AttributeError):
        print(f"Could not decode or parse event body. Raw event: {event}")
        # Fallback for simple string test invocations
        if isinstance(event, dict):
             ministry_name = event.get('ministry_name')
    
    if not ministry_name:
        print(f"ministry_name not found in event. Using failsafe: {DEFAULT_MINISTRY_NAME_FAILSAFE}")
        ministry_name = DEFAULT_MINISTRY_NAME_FAILSAFE
        # For a production system, you might want to return a 400 error here instead.
        # return {'statusCode': 400, 'body': json.dumps({'error': 'ministry_name is required'})}
    
    search_results = perform_web_search(ministry_name)
    if not search_results:
        return {'statusCode': 500, 'body': json.dumps({'error': 'Failed to perform web search'})}
    
    extracted_data = extract_handle_with_ai(search_results, ministry_name)
    
    # This is the final JSON response
    return {
        'statusCode': 200,
        'body': json.dumps(extracted_data)
    }