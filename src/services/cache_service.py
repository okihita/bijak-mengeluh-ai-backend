import time
import logging
from typing import Optional, Dict
import boto3
from botocore.config import Config

from config import settings

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        retry_config = Config(retries={'max_attempts': 5, 'mode': 'adaptive'})
        dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION, config=retry_config)
        self.table = dynamodb.Table(settings.CACHE_TABLE_NAME)
    
    def get(self, ministry_name: str) -> Optional[Dict[str, str]]:
        """Retrieves a cached social handle for a ministry."""
        try:
            logger.info(f"Checking cache for '{ministry_name}'")
            response = self.table.get_item(Key={'ministry_name': ministry_name})
            if 'Item' in response:
                logger.info(f"CACHE HIT for '{ministry_name}'")
                return response['Item']
        except Exception as e:
            logger.warning(f"Error reading from cache: {e}")
        
        logger.info(f"CACHE MISS for '{ministry_name}'")
        return None
    
    def put(self, ministry_name: str, handle: str, status: str = 'verified'):
        """Caches a social handle for a ministry."""
        logger.info(f"Caching handle for '{ministry_name}'")
        try:
            self.table.put_item(
                Item={
                    'ministry_name': ministry_name,
                    'handle': handle,
                    'status': status,
                    'cached_at': int(time.time())
                }
            )
        except Exception as e:
            logger.error(f"Error writing to cache: {e}")
