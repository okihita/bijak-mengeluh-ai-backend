import json
import logging
from typing import Dict
import boto3
from botocore.config import Config

from config import settings
from services.cache_service import CacheService

logger = logging.getLogger(__name__)

class SocialLookupService:
    def __init__(self):
        retry_config = Config(retries={'max_attempts': 5, 'mode': 'adaptive'})
        self.lambda_client = boto3.client('lambda', region_name=settings.AWS_REGION, config=retry_config)
        self.cache = CacheService()
    
    def _invoke_finder_lambda(self, ministry_name: str) -> Dict[str, str]:
        """Invokes the finder Lambda function to search for a social handle."""
        logger.info(f"Invoking finder Lambda for '{ministry_name}'")
        try:
            payload = json.dumps({"ministry_name": ministry_name})
            response = self.lambda_client.invoke(
                FunctionName=settings.FINDER_FUNCTION_NAME,
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
    
    def get_social_handle(self, ministry_name: str) -> Dict[str, str]:
        """
        Retrieves a ministry's social media handle using cache-aside pattern.
        1. Check cache
        2. If miss, invoke finder Lambda
        3. Cache high-confidence results
        """
        # Check cache first
        cached_item = self.cache.get(ministry_name)
        if cached_item:
            return {"handle": cached_item['handle'], "status": cached_item['status']}
        
        # Cache miss - invoke finder
        finder_result = self._invoke_finder_lambda(ministry_name)
        handle = finder_result.get('handle')
        confidence = finder_result.get('confidence')
        
        # Cache high/medium confidence results
        if handle and handle != 'NOT_FOUND' and confidence in ['high', 'medium']:
            status = 'verified' if confidence == 'high' else 'unverified'
            if status == 'verified':
                self.cache.put(ministry_name, handle, status)
            return {"handle": handle, "status": status}
        
        return {"handle": "NOT_FOUND", "status": finder_result.get("status", "none")}
