#!/usr/bin/env python3
"""
Scrape DKI Jakarta agencies with LLM verification
"""
import json
import os
import time
from decimal import Decimal
from typing import Dict, List
import boto3
import requests

# Configuration
SERPER_API_KEY = os.getenv('SERPER_API_KEY')
AWS_REGION = os.getenv('AWS_REGION', 'ap-southeast-2')
TABLE_NAME = os.getenv('AGENCIES_TABLE_NAME', 'agencies')

# DKI Jakarta agencies
DKI_PROVINCIAL_DINAS = [
    "Dinas Kesehatan",
    "Dinas Perhubungan", 
    "Dinas Pekerjaan Umum",
    "Dinas Pendidikan",
    "Dinas Sosial",
    "Dinas Lingkungan Hidup",
    "Dinas Perumahan",
    "Dinas Perindustrian",
    "Dinas Perdagangan",
    "Dinas Pariwisata",
    "Dinas Kebudayaan",
    "Dinas Pemuda dan Olahraga",
    "Dinas Ketahanan Pangan",
    "Dinas Kependudukan",
    "Dinas Komunikasi dan Informatika"
]

DKI_CITIES = [
    "Jakarta Pusat",
    "Jakarta Utara", 
    "Jakarta Barat",
    "Jakarta Selatan",
    "Jakarta Timur"
]

# Keywords mapping
KEYWORDS_MAP = {
    "Kesehatan": ["kesehatan", "rumah", "sakit", "puskesmas", "vaksin", "covid", "dokter", "obat", "rs", "hospital"],
    "Perhubungan": ["transportasi", "transjakarta", "busway", "parkir", "tilang", "macet", "bus", "angkot"],
    "Pekerjaan Umum": ["jalan", "rusak", "infrastruktur", "drainase", "banjir", "trotoar", "lampu", "jembatan", "gorong"],
    "Pendidikan": ["sekolah", "guru", "siswa", "ujian", "ppdb", "pendidikan"],
    "Sosial": ["bantuan", "sosial", "bansos", "pkh", "lansia", "disabilitas"],
    "Lingkungan Hidup": ["sampah", "kebersihan", "polusi", "limbah", "taman", "lingkungan"],
    "Perumahan": ["rumah", "rusun", "sewa", "kpr", "perumahan", "hunian"],
    "Perindustrian": ["industri", "pabrik", "izin", "usaha", "umkm"],
    "Perdagangan": ["pasar", "pedagang", "pkl", "harga", "sembako", "dagang"],
    "Pariwisata": ["wisata", "hotel", "tempat", "monas", "ancol", "tourism"],
    "Kebudayaan": ["budaya", "museum", "seni", "festival", "kebudayaan"],
    "Pemuda dan Olahraga": ["olahraga", "gor", "lapangan", "pemuda", "sport"],
    "Ketahanan Pangan": ["pangan", "beras", "sembako", "harga", "makanan"],
    "Kependudukan": ["ktp", "kk", "akta", "dukcapil", "e-ktp", "kartu", "keluarga"],
    "Komunikasi dan Informatika": ["internet", "wifi", "website", "aplikasi", "digital", "kominfo"]
}


def search_agency(agency_name: str, location: str = "DKI Jakarta") -> Dict:
    """Search for agency information using Serper API"""
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    
    queries = [
        f"{agency_name} {location} official website",
        f"{agency_name} {location} twitter instagram",
        f"{agency_name} {location} kontak telepon"
    ]
    
    results = {}
    for query in queries:
        payload = {"q": query, "num": 5}
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            results[query] = response.json()
        time.sleep(0.5)  # Rate limiting
    
    return results


def verify_with_llm(agency_name: str, location: str, search_results: Dict) -> Dict:
    """Use Bedrock to verify official accounts"""
    bedrock = boto3.client('bedrock-runtime', region_name=AWS_REGION)
    
    prompt = f"""Analyze these search results for {agency_name} {location}.

Search Results:
{json.dumps(search_results, indent=2)}

Task: Extract ONLY official government accounts and contact info.

Rules:
- Twitter: Must have @handle format, prefer verified or high followers
- Instagram: Must have @handle format
- Website: Must be .go.id domain or official government site
- Phone: Must be valid Indonesian number
- Reject parody, fan, or unofficial accounts

Return JSON:
{{
  "twitter": "@handle or null",
  "instagram": "@handle or null", 
  "facebook": "page_name or null",
  "website": "url or null",
  "phone": "number or null",
  "email": "email or null",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}}"""

    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-haiku-20240307-v1:0',
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        })
    )
    
    result = json.loads(response['body'].read())
    content = result['content'][0]['text']
    
    # Extract JSON from response
    start = content.find('{')
    end = content.rfind('}') + 1
    return json.loads(content[start:end])


def generate_agency_id(name: str, location: str) -> str:
    """Generate unique agency ID"""
    parts = location.lower().replace(" ", "-")
    name_parts = name.lower().replace("dinas ", "").replace(" ", "-")
    return f"{parts}-{name_parts}"


def extract_keywords(agency_name: str) -> List[str]:
    """Extract keywords for agency"""
    for key, keywords in KEYWORDS_MAP.items():
        if key.lower() in agency_name.lower():
            return keywords
    return []


def store_agency(agency_data: Dict):
    """Store agency in DynamoDB"""
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table(TABLE_NAME)
    
    # Store main record
    table.put_item(Item=agency_data)
    
    # Store keyword index entries
    for keyword in agency_data['keywords']:
        table.put_item(Item={
            'agency_id': f"keyword#{keyword}#{agency_data['agency_id']}",
            'keyword': keyword,
            'agency_ref': agency_data['agency_id']
        })
    
    print(f"✅ Stored: {agency_data['name']}")


def scrape_agency(name: str, location: str, level: str) -> Dict:
    """Scrape single agency"""
    print(f"\n🔍 Scraping: {name} - {location}")
    
    # Search
    search_results = search_agency(name, location)
    
    # Verify with LLM
    verified = verify_with_llm(name, location, search_results)
    
    # Build agency data
    agency_data = {
        'agency_id': generate_agency_id(name, location),
        'name': f"{name} {location}",
        'province': 'DKI Jakarta',
        'city': location if level == 'city' else None,
        'level': level,
        'keywords': extract_keywords(name),
        'social_media': {
            'twitter': verified.get('twitter'),
            'instagram': verified.get('instagram'),
            'facebook': verified.get('facebook')
        },
        'website': verified.get('website'),
        'phone': verified.get('phone'),
        'email': verified.get('email'),
        'confidence': Decimal(str(verified.get('confidence', 0.0))),
        'reasoning': verified.get('reasoning', ''),
        'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'updated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ')
    }
    
    return agency_data


def scrape_dki_jakarta():
    """Scrape all DKI Jakarta agencies"""
    agencies = []
    
    # Provincial level
    print("\n" + "="*50)
    print("SCRAPING PROVINCIAL DINAS")
    print("="*50)
    
    for dinas in DKI_PROVINCIAL_DINAS:
        try:
            agency = scrape_agency(dinas, "DKI Jakarta", "provincial")
            agencies.append(agency)
            store_agency(agency)
            time.sleep(1)  # Rate limiting
        except Exception as e:
            print(f"❌ Error: {dinas} - {e}")
    
    # Municipal level
    print("\n" + "="*50)
    print("SCRAPING MUNICIPAL DINAS")
    print("="*50)
    
    for city in DKI_CITIES:
        print(f"\n📍 {city}")
        for dinas in DKI_PROVINCIAL_DINAS:
            try:
                agency = scrape_agency(dinas, city, "city")
                agencies.append(agency)
                store_agency(agency)
                time.sleep(1)
            except Exception as e:
                print(f"❌ Error: {dinas} {city} - {e}")
    
    # Save to file
    with open('dki_agencies.json', 'w') as f:
        json.dump(agencies, f, indent=2)
    
    print(f"\n✅ Scraped {len(agencies)} agencies")
    print(f"📁 Saved to: dki_agencies.json")
    
    return agencies


if __name__ == '__main__':
    if not SERPER_API_KEY:
        print("❌ Error: SERPER_API_KEY not set")
        print("Get free API key: https://serper.dev")
        exit(1)
    
    scrape_dki_jakarta()
