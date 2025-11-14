import json
import logging
from typing import List, Dict, Any
import boto3
from botocore.config import Config

from config import settings, prompts

logger = logging.getLogger(__name__)

class BedrockService:
    def __init__(self):
        retry_config = Config(retries={'max_attempts': 5, 'mode': 'adaptive'})
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name=settings.AWS_REGION,
            config=retry_config
        )
    
    def _invoke_model(self, model_id: str, body: Dict[str, Any]) -> Dict[str, Any]:
        """Invokes a Bedrock model and returns the parsed JSON response."""
        logger.info(f"Invoking Bedrock model: {model_id}")
        try:
            response = self.client.invoke_model(
                body=json.dumps(body),
                modelId=model_id,
                accept='application/json',
                contentType='application/json'
            )
            response_body = json.loads(response.get('body').read())
            logger.info("Successfully received response from model")
            return response_body
        except Exception as e:
            logger.error(f"Error invoking Bedrock model {model_id}: {e}", exc_info=True)
            return {}
    
    def get_embedding(self, text: str) -> List[float]:
        """Generates an embedding for the given text."""
        logger.info(f"Getting embedding for text: '{text[:50]}...'")
        body = {"texts": [text], "input_type": "search_query"}
        response_body = self._invoke_model(settings.BEDROCK_EMBED_MODEL_ID, body)
        return response_body.get('embeddings', [[]])[0]
    
    def generate_complaint_text(self, user_prompt: str, tone: str = "formal") -> str:
        """Generates a complaint text from a user's prompt with specified tone."""
        logger.info(f"Generating complaint text with tone: {tone}")
        
        # Select prompt based on tone
        if tone == "funny":
            prompt_template = prompts.COMPLAINT_GENERATION_PROMPT_FUNNY
        elif tone == "angry":
            prompt_template = prompts.COMPLAINT_GENERATION_PROMPT_ANGRY
        else:  # default to formal
            prompt_template = prompts.COMPLAINT_GENERATION_PROMPT_FORMAL
        
        prompt = prompt_template.format(user_prompt=user_prompt)
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 512,  # Reduced from 1024 for cost optimization
            "messages": [{"role": "user", "content": prompt}]
        }
        response_body = self._invoke_model(settings.BEDROCK_GENERATE_MODEL_ID, body)
        if response_body and 'content' in response_body and response_body['content']:
            return response_body['content'][0].get('text', '').strip()
        return ""
    
    def generate_rationale(self, user_prompt: str, ministry_name: str, ministry_desc: str) -> str:
        """Generates a rationale for suggesting a specific ministry."""
        logger.info(f"Generating rationale for ministry: {ministry_name}")
        prompt = prompts.RATIONALE_GENERATION_PROMPT.format(
            user_prompt=user_prompt,
            ministry_name=ministry_name,
            ministry_desc=ministry_desc
        )
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 256,  # Reduced from 512 for cost optimization
            "messages": [{"role": "user", "content": prompt}]
        }
        response_body = self._invoke_model(settings.BEDROCK_GENERATE_MODEL_ID, body)
        if response_body and 'content' in response_body and response_body['content']:
            return response_body['content'][0].get('text', '').strip()
        return ""
