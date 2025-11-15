#!/usr/bin/env python3
"""Scrape 34 national ministries"""
import os
import time

# Ensure SERPER_API_KEY is set
if not os.getenv('SERPER_API_KEY'):
    raise ValueError("SERPER_API_KEY environment variable must be set")

from scrape_dki_agencies import scrape_agency, store_agency

NATIONAL_MINISTRIES = [
    ("Kementerian Dalam Negeri", ["ktp", "kk", "akta", "dukcapil", "pemda", "daerah"]),
    ("Kementerian Luar Negeri", ["paspor", "visa", "wni", "luar negeri", "kedutaan"]),
    ("Kementerian Pertahanan", ["tni", "militer", "pertahanan", "keamanan"]),
    ("Kementerian Hukum dan HAM", ["hukum", "ham", "penjara", "imigrasi", "notaris"]),
    ("Kementerian Keuangan", ["pajak", "bea cukai", "npwp", "keuangan", "anggaran"]),
    ("Kementerian Pertanian", ["pertanian", "petani", "pupuk", "pangan", "sawah"]),
    ("Kementerian Perindustrian", ["industri", "pabrik", "manufaktur", "izin usaha"]),
    ("Kementerian Energi dan Sumber Daya Mineral", ["listrik", "pln", "tambang", "migas", "energi"]),
    ("Kementerian Perhubungan", ["transportasi", "bandara", "pelabuhan", "kereta", "pesawat"]),
    ("Kementerian Pendidikan", ["sekolah", "universitas", "guru", "siswa", "kuliah"]),
    ("Kementerian Kesehatan", ["kesehatan", "rumah", "sakit", "puskesmas", "obat", "dokter"]),
    ("Kementerian Agama", ["agama", "haji", "umroh", "masjid", "gereja"]),
    ("Kementerian Ketenagakerjaan", ["kerja", "buruh", "upah", "phk", "bpjs ketenagakerjaan"]),
    ("Kementerian Sosial", ["sosial", "bansos", "pkh", "lansia", "disabilitas"]),
    ("Kementerian PUPR", ["jalan", "rusak", "infrastruktur", "banjir", "bendungan"]),
    ("Kementerian Agraria dan Tata Ruang", ["tanah", "sertifikat", "bpn", "agraria"]),
    ("Kementerian Lingkungan Hidup", ["lingkungan", "sampah", "polusi", "limbah", "hutan"]),
    ("Kementerian Komunikasi dan Digital", ["internet", "telkom", "provider", "digital", "kominfo"]),
    ("Kementerian BUMN", ["bumn", "pertamina", "pln", "telkom", "bri"]),
    ("Kementerian Koperasi dan UKM", ["koperasi", "ukm", "umkm", "usaha kecil"]),
    ("Kementerian Pariwisata", ["wisata", "hotel", "pariwisata", "tourism"]),
    ("Kementerian Pemuda dan Olahraga", ["olahraga", "pemuda", "gor", "atlet"]),
    ("Kementerian Kelautan dan Perikanan", ["laut", "nelayan", "ikan", "perikanan"]),
    ("Kementerian Kehutanan", ["hutan", "kebakaran", "illegal logging", "kehutanan"]),
    ("Kementerian Desa dan PDT", ["desa", "dana desa", "bumdes", "daerah tertinggal"]),
    ("Kementerian Pemberdayaan Perempuan", ["perempuan", "anak", "kdrt", "kekerasan"]),
    ("Kementerian Perencanaan Pembangunan", ["bappenas", "pembangunan", "perencanaan"]),
    ("Kementerian Riset dan Teknologi", ["riset", "penelitian", "teknologi", "inovasi"]),
    ("Kementerian Investasi", ["investasi", "modal", "investor", "penanaman modal"]),
    ("Kementerian Perdagangan", ["dagang", "ekspor", "impor", "perdagangan", "pasar"]),
    ("Kementerian Perumahan", ["rumah", "rusun", "perumahan", "subsidi rumah"]),
    ("Kepolisian Negara", ["polisi", "laporan", "kehilangan", "kejahatan", "tilang"]),
    ("Kejaksaan Agung", ["jaksa", "penuntutan", "korupsi", "pidana"]),
    ("Badan Pertanahan Nasional", ["tanah", "sertifikat", "bpn", "pertanahan"]),
]

print(f"\n{'='*60}")
print(f"SCRAPING {len(NATIONAL_MINISTRIES)} NATIONAL MINISTRIES")
print(f"{'='*60}\n")

scraped = 0
failed = []

for i, (ministry_name, keywords) in enumerate(NATIONAL_MINISTRIES, 1):
    try:
        print(f"[{i}/{len(NATIONAL_MINISTRIES)}] {ministry_name}...", end=" ", flush=True)
        
        # Use existing scraper but override keywords
        agency = scrape_agency(ministry_name, "Indonesia", "national")
        agency['keywords'] = keywords  # Override with our keywords
        agency['agency_id'] = ministry_name.lower().replace(" ", "-").replace("kementerian-", "kemenkementerian-")
        
        store_agency(agency)
        scraped += 1
        print("✅")
        
        time.sleep(1)  # Rate limiting
        
    except Exception as e:
        print(f"❌ {e}")
        failed.append(ministry_name)

print(f"\n{'='*60}")
print(f"✅ Scraped: {scraped}/{len(NATIONAL_MINISTRIES)}")
if failed:
    print(f"❌ Failed: {len(failed)}")
    for f in failed:
        print(f"   - {f}")
print(f"{'='*60}\n")
