import logging
from typing import List, Dict
from pinecone import Pinecone

from config import settings

logger = logging.getLogger(__name__)

class PineconeService:
    def __init__(self):
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = pc.Index(settings.PINECONE_INDEX_NAME)
    
    def find_relevant_ministries(self, embedding: List[float], top_k: int = 3) -> List[Dict]:
        """Queries Pinecone to find relevant government ministries."""
        logger.info(f"Querying Pinecone for top {top_k} matches")
        query_response = self.index.query(
            vector=embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        ministries = [
            {
                "name": match['metadata']['name'],
                "score": match['score'],
                "description": match['metadata'].get('text_content', '')
            }
            for match in query_response.get('matches', [])
        ]
        
        logger.info(f"Found ministries: {[m['name'] for m in ministries]}")
        return ministries
