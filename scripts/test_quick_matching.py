#!/usr/bin/env python3
"""Quick matching test with 3 scraped agencies"""
import boto3

AWS_REGION = 'ap-southeast-2'

# Test cases for the 3 agencies we scraped
TEST_CASES = [
    ("Puskesmas tutup di Jakarta", "dki-jakarta-kesehatan"),
    ("Rumah sakit penuh", "dki-jakarta-kesehatan"),
    ("Vaksin COVID habis", "dki-jakarta-kesehatan"),
    ("Transjakarta mogok di Jakarta Selatan", "jakarta-selatan-perhubungan"),
    ("Busway penuh di Jaksel", "jakarta-selatan-perhubungan"),
    ("Jalan rusak di Jakarta Pusat", "jakarta-pusat-pekerjaan-umum"),
    ("Trotoar hancur di Jakpus", "jakarta-pusat-pekerjaan-umum"),
]

def match_agency(complaint: str):
    """Match complaint to agency"""
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table('agencies')
    
    # Extract keywords
    tokens = complaint.lower().split()
    keywords = [t for t in tokens if len(t) > 3]
    
    # Query for each keyword
    matches = {}
    for keyword in keywords:
        try:
            response = table.query(
                IndexName='keyword-index',
                KeyConditionExpression='keyword = :kw',
                ExpressionAttributeValues={':kw': keyword}
            )
            for item in response.get('Items', []):
                agency_id = item.get('agency_ref', item.get('agency_id'))
                if agency_id and not agency_id.startswith('keyword#'):
                    matches[agency_id] = matches.get(agency_id, 0) + 1
        except:
            pass
    
    if not matches:
        return None, 0.0
    
    # Get top match
    top_match = max(matches.items(), key=lambda x: x[1])
    agency_id = top_match[0]
    score = top_match[1] / len(keywords) if keywords else 0
    
    return agency_id, score

def test_matching():
    """Test matching accuracy"""
    print("\n" + "="*60)
    print("QUICK MATCHING TEST (3 agencies)")
    print("="*60 + "\n")
    
    correct = 0
    total = len(TEST_CASES)
    
    for i, (complaint, expected_id) in enumerate(TEST_CASES, 1):
        matched_id, score = match_agency(complaint)
        is_correct = matched_id == expected_id
        
        if is_correct:
            correct += 1
        
        status = "✅" if is_correct else "❌"
        print(f"{status} {i}. {complaint}")
        print(f"   Expected: {expected_id}")
        print(f"   Matched:  {matched_id} (score: {score:.2f})")
        print()
    
    accuracy = (correct / total) * 100
    
    print("="*60)
    print(f"Results: {correct}/{total} correct ({accuracy:.0f}%)")
    print("="*60)
    
    if accuracy >= 85:
        print("\n✅ Matching works! Ready for full scrape.")
        return True
    else:
        print("\n⚠️  Need to tune keywords before full scrape.")
        return False

if __name__ == '__main__':
    test_matching()
