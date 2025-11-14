#!/usr/bin/env python3
"""Test scraper with 3 agencies"""
import os
os.environ['SERPER_API_KEY'] = '844a99ba96ce92fa47ad538acc0edb6527996d5c'

from scrape_dki_agencies import scrape_agency, store_agency

# Test with 3 agencies
test_agencies = [
    ("Dinas Kesehatan", "DKI Jakarta", "provincial"),
    ("Dinas Perhubungan", "Jakarta Selatan", "city"),
    ("Dinas Pekerjaan Umum", "Jakarta Pusat", "city"),
]

print("Testing scraper with 3 agencies...\n")

for name, location, level in test_agencies:
    try:
        agency = scrape_agency(name, location, level)
        store_agency(agency)
        print(f"✅ Success: {agency['name']}\n")
    except Exception as e:
        print(f"❌ Error: {name} {location} - {e}\n")

print("Test complete!")
