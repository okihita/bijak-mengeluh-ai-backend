#!/usr/bin/env python3
"""Scrape remaining 16 national ministries"""
import os
os.environ['SERPER_API_KEY'] = '844a99ba96ce92fa47ad538acc0edb6527996d5c'

from scrape_dki_agencies import scrape_agency, store_agency
import time

REMAINING_MINISTRIES = [
    ("Kementerian PUPR", ["jalan", "rusak", "infrastruktur", "banjir", "bendungan", "drainase"]),
    ("Kementerian Pariwisata", ["wisata", "hotel", "pariwisata", "tourism", "tempat wisata"]),
    ("Kementerian Kelautan dan Perikanan", ["laut", "nelayan", "ikan", "perikanan", "kapal"]),
    ("Kementerian Kehutanan", ["hutan", "kebakaran", "illegal logging", "kehutanan", "kayu"]),
    ("Kementerian Desa dan PDT", ["desa", "dana desa", "bumdes", "daerah tertinggal"]),
    ("Kementerian Pemberdayaan Perempuan", ["perempuan", "anak", "kdrt", "kekerasan", "perlindungan"]),
    ("Kementerian Perencanaan Pembangunan", ["bappenas", "pembangunan", "perencanaan", "anggaran"]),
    ("Kementerian Riset dan Teknologi", ["riset", "penelitian", "teknologi", "inovasi", "sains"]),
    ("Kementerian Investasi", ["investasi", "modal", "investor", "penanaman modal", "bkpm"]),
    ("Kementerian Perdagangan", ["dagang", "ekspor", "impor", "perdagangan", "pasar", "harga"]),
    ("Kementerian Perumahan", ["rumah", "rusun", "perumahan", "subsidi rumah", "kpr"]),
    ("Kepolisian Negara", ["polisi", "laporan", "kehilangan", "kejahatan", "tilang", "polri"]),
    ("Kejaksaan Agung", ["jaksa", "penuntutan", "korupsi", "pidana", "kejaksaan"]),
    ("Badan Pertanahan Nasional", ["tanah", "sertifikat", "bpn", "pertanahan", "atm"]),
    ("Kementerian Keuangan", ["pajak", "bea cukai", "npwp", "keuangan", "anggaran", "kemenkeu"]),
    ("Kementerian Hukum dan HAM", ["hukum", "ham", "penjara", "imigrasi", "notaris", "kemenkumham"]),
]

print(f"\n{'='*60}")
print(f"SCRAPING {len(REMAINING_MINISTRIES)} REMAINING NATIONAL MINISTRIES")
print(f"{'='*60}\n")

scraped = 0
failed = []

for i, (ministry_name, keywords) in enumerate(REMAINING_MINISTRIES, 1):
    try:
        print(f"[{i}/{len(REMAINING_MINISTRIES)}] {ministry_name}...", end=" ", flush=True)
        
        agency = scrape_agency(ministry_name, "Indonesia", "national")
        agency['keywords'] = keywords
        agency['agency_id'] = ministry_name.lower().replace(" ", "-").replace("kementerian-", "kemen-")
        
        store_agency(agency)
        scraped += 1
        print("✅")
        
        time.sleep(1)
        
    except Exception as e:
        print(f"❌ {e}")
        failed.append(ministry_name)

print(f"\n{'='*60}")
print(f"✅ Scraped: {scraped}/{len(REMAINING_MINISTRIES)}")
if failed:
    print(f"❌ Failed: {len(failed)}")
    for f in failed:
        print(f"   - {f}")
print(f"{'='*60}\n")

# Final count
import boto3
dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
table = dynamodb.Table('agencies')
response = table.scan(Select='COUNT', FilterExpression='attribute_not_exists(keyword)')
total = response['Count']

print(f"🎉 TOTAL AGENCIES IN DATABASE: {total}")
print(f"   - DKI Jakarta: ~87")
print(f"   - National: ~{total - 87}")
