"""
DynamoDB-based agency matching service
Replaces Pinecone for cost optimization
"""
import boto3
from typing import List, Dict, Tuple

class DynamoDBMatcher:
    def __init__(self, region='ap-southeast-2'):
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table('agencies')
    
    def match_agencies(self, complaint_text: str, top_k: int = 3) -> List[Dict]:
        """
        Match complaint to agencies using keyword matching
        
        Args:
            complaint_text: User's complaint
            top_k: Number of top matches to return
            
        Returns:
            List of matched agencies with scores
        """
        # Extract keywords (simple tokenization)
        tokens = complaint_text.lower().split()
        keywords = [t for t in tokens if len(t) > 3]
        
        if not keywords:
            return []
        
        # Query DynamoDB for each keyword
        matches = {}
        for keyword in keywords:
            try:
                response = self.table.query(
                    IndexName='keyword-index',
                    KeyConditionExpression='keyword = :kw',
                    ExpressionAttributeValues={':kw': keyword}
                )
                
                for item in response.get('Items', []):
                    agency_id = item.get('agency_ref', item.get('agency_id'))
                    if agency_id and not agency_id.startswith('keyword#'):
                        matches[agency_id] = matches.get(agency_id, 0) + 1
            except Exception as e:
                print(f"Error querying keyword {keyword}: {e}")
                continue
        
        if not matches:
            return []
        
        # Sort by match count
        sorted_matches = sorted(matches.items(), key=lambda x: x[1], reverse=True)
        
        # Fetch full agency details for top matches
        results = []
        for agency_id, match_count in sorted_matches[:top_k]:
            try:
                response = self.table.get_item(Key={'agency_id': agency_id})
                if 'Item' in response:
                    agency = response['Item']
                    score = match_count / len(keywords)
                    
                    results.append({
                        'name': agency.get('name', ''),
                        'score': float(score),
                        'description': f"{agency.get('level', '')} level agency",
                        'social_media': agency.get('social_media', {}),
                        'website': agency.get('website'),
                        'phone': agency.get('phone'),
                        'email': agency.get('email')
                    })
            except Exception as e:
                print(f"Error fetching agency {agency_id}: {e}")
                continue
        
        return results
