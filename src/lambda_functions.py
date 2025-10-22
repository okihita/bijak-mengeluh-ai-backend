import os
import json
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Bedrock client (outside handler for reuse)
bedrock_runtime = boto3.client(service_name='bedrock-runtime', region_name='ap-southeast-2') # Or your Bedrock region

# Get allowed origins from environment variables
allowed_origins = [
    os.environ.get('ALLOWED_ORIGIN_PROD'),
    os.environ.get('ALLOWED_ORIGIN_DEV')
]

logger.info(f"Allowed origins from env: {allowed_origins}")

# Filter out None values in case env vars aren't set
allowed_origins = [origin for origin in allowed_origins if origin]

def lambda_handler(event, context):

    logger.info(f"Received event: {json.dumps(event)}")

    # --- CORS Preflight Handling ---
    origin = event.get('headers', {}).get('origin')
    logger.info(f"Request Origin: {origin}")

    # Determine allowed origin for the response header
    response_origin = None
    logger.info(f"Response origin is set to None")
    if origin in allowed_origins:
        logger.info(f"Origin {origin} is allowed.")
        response_origin = origin
    elif not allowed_origins: # Fallback if no env vars set (less secure)
        logger.info("No allowed origins set; allowing all origins.")
        response_origin = '*'

    # Default headers (adjust Allowed-Methods/Headers if needed)
    cors_headers = {
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS,POST',
    }
    if response_origin:
         logger.info(f"Setting Access-Control-Allow-Origin to {response_origin}")
         cors_headers['Access-Control-Allow-Origin'] = response_origin


    # If it's an OPTIONS request (preflight), return CORS headers immediately
    if event['requestContext']['http']['method'] == 'OPTIONS':
        logger.info("Handling OPTIONS preflight request.")
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps('CORS Preflight OK')
        }
    
    # --- Regular POST Request Handling ---
    try:
        body = json.loads(event.get('body', '{}'))
        user_prompt = body.get('prompt')

        if not user_prompt:
            return {
                'statusCode': 400,
                'headers': cors_headers, # Include CORS headers in all responses
                'body': json.dumps({'error': 'Prompt is missing'})
            }

        # ... (rest of your Bedrock logic: prompt, request_body, invoke_model) ...

        prompt = f"Based on the following user complaint, please write a clear, polite, and detailed formal complaint suitable for submission to a government agency in Indonesia. The user's input is: '{user_prompt}'"
        request_body = {
             "anthropic_version": "bedrock-2023-05-31",
             "max_tokens": 1024,
             "messages": [{"role": "user", "content": prompt}]
        }
        response = bedrock_runtime.invoke_model(
             body=json.dumps(request_body),
             modelId='anthropic.claude-3-haiku-20240307-v1:0', # Or Haiku if you switched
             accept='application/json',
             contentType='application/json'
        )
        response_body = json.loads(response.get('body').read())
        generated_text = response_body['content'][0]['text']


        return {
            'statusCode': 200,
            'headers': cors_headers, # Include CORS headers
            'body': json.dumps({'generated_text': generated_text})
        }

    except Exception as e:
        print(f"Error: {e}") # Log the specific error to CloudWatch
        logger.error(f"Error: {e}")
        # Extract relevant info if possible, but avoid sending raw exception to client
        error_message = f"Internal server error processing prompt."
        return {
            'statusCode': 500,
            'headers': cors_headers, # Include CORS headers
            'body': json.dumps({'error': error_message})
        }