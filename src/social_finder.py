import boto3
import json
import os
import requests

# --- Initialization ---
SERPER_API_KEY = os.environ["SERPER_API_KEY"]
AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-2")
BEDROCK_GENERATE_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0" # Claude Sonnet
BEDROCK_GENERATE_MODEL_ID = os.environ.get("BEDROCK_GENERATE_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")

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
        
        # Concatenate snippets for the AI to analyze
        search_snippets = ""
        for item in results.get('organic', []):
            snippet = item.get('snippet', '')
            title = item.get('title', '')
            link = item.get('link', '')
            # We provide a clean, structured context for the LLM
            search_snippets += f"<result>\n<title>{title}</title>\n<link>{link}</link>\n<snippet>{snippet}</snippet>\n</result>\n"
            
        print(f"Search results: {search_snippets}")
        return search_snippets
        
    except requests.exceptions.RequestException as e:
        print(f"Error during Serper API call: {e}")
        return None

def extract_handle_with_ai(search_results, ministry_name):
    """
    Uses Claude Sonnet to read the search results and extract the official handle.
    This is far more robust than simple regex.
    """
    print("Extracting handle with AI...")
    
    # This is a powerful extraction prompt
    prompt = f"""Human: I have performed a web search for the official X/Twitter handle for "{ministry_name}".
Your task is to analyze the following search result snippets and extract *only* the official, verified X/Twitter handle (which must start with '@').

<search_results>
{search_results}
</search_results>

Guidelines:
1.  Look for handles mentioned in official-looking titles or snippets (e.g., "KemenPUPR (@KemenPU)", "Official X for...").
2.  Prioritize handles from `twitter.com` or `x.com` links.
3.  If multiple handles are found, choose the one that seems most official and relevant to the ministry's name.
4.  If no plausible, official handle is found, you MUST return the string "NOT_FOUND".
5.  Do not add any explanation. Respond with *only* the handle (e.g., "@KemenPU") or "NOT_FOUND".

Official Handle:
Assistant:"""

    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 50, # We only need one word
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
        handle = response_body['content'][0]['text'].strip()
        
        # Final validation
        if not handle.startswith('@') or len(handle) < 4:
            print(f"AI returned an invalid handle ('{handle}') or 'NOT_FOUND'.")
            return "NOT_FOUND"
        
        print(f"AI extracted handle: {handle}")
        return handle
        
    except Exception as e:
        print(f"Error during Bedrock extraction call: {e}")
        return "NOT_FOUND"

def lambda_handler(event, context):
    """
    This function is designed to be invoked by the Bedrock Agent.
    The event will contain the ministry name.
    """
    print(f"Received event: {event}")
    
    # This is for manual testing from the Lambda console
    # The agent will send a different, more complex payload tomorrow
    ministry_name = event.get('ministry_name', 'Kementerian PUPR') # Default for testing

    if not ministry_name:
        return {'statusCode': 400, 'body': json.dumps({'error': 'ministry_name is missing'})}

    search_results = perform_web_search(ministry_name)
    
    if not search_results:
        return {'statusCode': 500, 'body': json.dumps({'error': 'Failed to perform web search'})}
    
    handle = extract_handle_with_ai(search_results, ministry_name)
    
    # This is the final JSON response
    return {
        'statusCode': 200,
        'body': json.dumps({
            'ministry_name': ministry_name,
            'social_media_handle': handle
        })
    }