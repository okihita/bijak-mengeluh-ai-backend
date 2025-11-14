# DKI Jakarta Agency Scraping

## Setup

### 1. Get Serper API Key (FREE)
```bash
# Visit: https://serper.dev
# Sign up (free tier: 2,500 queries/month)
# Copy API key
export SERPER_API_KEY="your_key_here"
```

### 2. Install Dependencies
```bash
pip install boto3 requests
```

### 3. Configure AWS
```bash
aws configure --profile bijak-mengeluh-aws-iam
# Region: ap-southeast-2
```

## Usage

### Step 1: Create DynamoDB Table
```bash
python create_agencies_table.py
```

Expected output:
```
✅ Table created: agencies
```

### Step 2: Scrape DKI Jakarta Agencies
```bash
export SERPER_API_KEY="your_key_here"
python scrape_dki_agencies.py
```

Expected output:
```
==================================================
SCRAPING PROVINCIAL DINAS
==================================================

🔍 Scraping: Dinas Kesehatan - DKI Jakarta
✅ Stored: Dinas Kesehatan DKI Jakarta

...

✅ Scraped 90 agencies
📁 Saved to: dki_agencies.json
```

**Time:** ~45 minutes  
**Cost:** ~$0.03

### Step 3: Test Matching Accuracy
```bash
python test_matching_accuracy.py
```

Expected output:
```
==================================================
TESTING MATCHING ACCURACY
==================================================
Total test cases: 50
Target accuracy: >95%
==================================================

✅ Case  1: Puskesmas tutup di Jakarta Pusat | Score: 0.85
✅ Case  2: Rumah sakit penuh di Jakarta Selatan | Score: 0.90
...

==================================================
RESULTS
==================================================
Correct:  48/50
Accuracy: 96.0%
Target:   95.0%
Status:   ✅ PASS
==================================================

🎉 Matching accuracy validated!
✅ Ready for production deployment
```

## Files Generated

- `dki_agencies.json` - All scraped agencies
- `matching_test_results.json` - Test results with metrics

## Cost Breakdown

| Component | Cost |
|-----------|------|
| Serper API | $0 (free tier) |
| Bedrock LLM | $0.02 |
| DynamoDB | $0.01 |
| **Total** | **$0.03** |

## Troubleshooting

### Error: SERPER_API_KEY not set
```bash
export SERPER_API_KEY="your_key_here"
```

### Error: Table already exists
```bash
# Delete existing table
aws dynamodb delete-table --table-name agencies --region ap-southeast-2
# Wait 30 seconds, then recreate
python create_agencies_table.py
```

### Low accuracy (<95%)
1. Check `matching_test_results.json` for failures
2. Add missing keywords to `KEYWORDS_MAP` in scraper
3. Re-run scraper for failed agencies
4. Re-test

## Next Steps

After validation:
1. Deploy to production Lambda
2. Update frontend to use DynamoDB matching
3. Remove Pinecone dependency
4. Save $70/month 🎉
