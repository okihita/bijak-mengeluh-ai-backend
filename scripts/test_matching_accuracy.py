#!/usr/bin/env python3
"""
Test matching accuracy with comprehensive test cases
Target: >95% accuracy (stop at diminishing returns)
"""
import json
from typing import Dict, List, Tuple
import boto3

AWS_REGION = 'ap-southeast-2'

# Comprehensive test cases (50 cases for high accuracy)
TEST_CASES = [
    # Health (Kesehatan) - 10 cases
    ("Puskesmas tutup di Jakarta Pusat", "jakarta-pusat-kesehatan", "city"),
    ("Rumah sakit penuh di Jakarta Selatan", "jakarta-selatan-kesehatan", "city"),
    ("Vaksin COVID habis di Jakarta Timur", "jakarta-timur-kesehatan", "city"),
    ("Dokter tidak ada di puskesmas Jakarta Barat", "jakarta-barat-kesehatan", "city"),
    ("Obat mahal di apotek Jakarta Utara", "jakarta-utara-kesehatan", "city"),
    ("Pelayanan kesehatan buruk di DKI", "dki-jakarta-kesehatan", "provincial"),
    ("BPJS tidak bisa dipakai di puskesmas", "dki-jakarta-kesehatan", "provincial"),
    ("Antrian rumah sakit lama sekali", "dki-jakarta-kesehatan", "provincial"),
    ("Imunisasi anak terlambat", "dki-jakarta-kesehatan", "provincial"),
    ("Posyandu tidak aktif", "dki-jakarta-kesehatan", "provincial"),
    
    # Transportation (Perhubungan) - 10 cases
    ("Transjakarta mogok di Jakarta Selatan", "jakarta-selatan-perhubungan", "city"),
    ("Busway penuh sesak di Jakarta Pusat", "jakarta-pusat-perhubungan", "city"),
    ("Parkir liar di Jakarta Barat", "jakarta-barat-perhubungan", "city"),
    ("Tilang sembarangan di Jakarta Timur", "jakarta-timur-perhubungan", "city"),
    ("Macet parah di Jakarta Utara", "jakarta-utara-perhubungan", "city"),
    ("Halte rusak tidak diperbaiki", "dki-jakarta-perhubungan", "provincial"),
    ("Tarif transjakarta naik terus", "dki-jakarta-perhubungan", "provincial"),
    ("Sopir busway ugal-ugalan", "dki-jakarta-perhubungan", "provincial"),
    ("Jalur sepeda tidak terawat", "dki-jakarta-perhubungan", "provincial"),
    ("Rambu lalu lintas hilang", "dki-jakarta-perhubungan", "provincial"),
    
    # Public Works (PU) - 10 cases
    ("Jalan rusak berlubang di Jakarta Selatan", "jakarta-selatan-pekerjaan-umum", "city"),
    ("Trotoar hancur di Jakarta Pusat", "jakarta-pusat-pekerjaan-umum", "city"),
    ("Drainase mampet banjir di Jakarta Timur", "jakarta-timur-pekerjaan-umum", "city"),
    ("Lampu jalan mati di Jakarta Barat", "jakarta-barat-pekerjaan-umum", "city"),
    ("Jembatan retak di Jakarta Utara", "jakarta-utara-pekerjaan-umum", "city"),
    ("Infrastruktur jalan buruk", "dki-jakarta-pekerjaan-umum", "provincial"),
    ("Perbaikan jalan lama sekali", "dki-jakarta-pekerjaan-umum", "provincial"),
    ("Gorong-gorong tersumbat", "dki-jakarta-pekerjaan-umum", "provincial"),
    ("Jalan berlubang tidak ditambal", "dki-jakarta-pekerjaan-umum", "provincial"),
    ("Banjir karena drainase rusak", "dki-jakarta-pekerjaan-umum", "provincial"),
    
    # Education (Pendidikan) - 5 cases
    ("PPDB tidak transparan di Jakarta Selatan", "jakarta-selatan-pendidikan", "city"),
    ("Sekolah kekurangan guru di Jakarta Timur", "jakarta-timur-pendidikan", "city"),
    ("Fasilitas sekolah rusak di Jakarta Pusat", "jakarta-pusat-pendidikan", "city"),
    ("Biaya sekolah mahal", "dki-jakarta-pendidikan", "provincial"),
    ("Kurikulum tidak jelas", "dki-jakarta-pendidikan", "provincial"),
    
    # Social (Sosial) - 5 cases
    ("Bantuan sosial tidak tepat sasaran di Jakarta Barat", "jakarta-barat-sosial", "city"),
    ("PKH terlambat cair di Jakarta Utara", "jakarta-utara-sosial", "city"),
    ("Lansia tidak dapat bantuan", "dki-jakarta-sosial", "provincial"),
    ("Penyandang disabilitas diabaikan", "dki-jakarta-sosial", "provincial"),
    ("Bansos tidak merata", "dki-jakarta-sosial", "provincial"),
    
    # Environment (Lingkungan Hidup) - 5 cases
    ("Sampah menumpuk di Jakarta Selatan", "jakarta-selatan-lingkungan-hidup", "city"),
    ("Taman tidak terawat di Jakarta Pusat", "jakarta-pusat-lingkungan-hidup", "city"),
    ("Polusi udara parah", "dki-jakarta-lingkungan-hidup", "provincial"),
    ("Limbah pabrik mencemari", "dki-jakarta-lingkungan-hidup", "provincial"),
    ("Kebersihan kota buruk", "dki-jakarta-lingkungan-hidup", "provincial"),
    
    # Population (Kependudukan) - 5 cases
    ("E-KTP belum jadi di Jakarta Timur", "jakarta-timur-kependudukan", "city"),
    ("Akta kelahiran susah diurus di Jakarta Barat", "jakarta-barat-kependudukan", "city"),
    ("Kartu keluarga hilang sulit diganti", "dki-jakarta-kependudukan", "provincial"),
    ("Pelayanan dukcapil lambat", "dki-jakarta-kependudukan", "provincial"),
    ("KTP rusak tidak bisa diganti", "dki-jakarta-kependudukan", "provincial"),
]


def match_agency(complaint: str) -> Tuple[str, float]:
    """Match complaint to agency using keyword matching"""
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table('agencies')
    
    # Extract keywords from complaint
    tokens = complaint.lower().split()
    keywords = [t for t in tokens if len(t) > 3]
    
    # Query DynamoDB for each keyword
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


def test_matching_accuracy():
    """Test matching accuracy with comprehensive cases"""
    print("\n" + "="*60)
    print("TESTING MATCHING ACCURACY")
    print("="*60)
    print(f"Total test cases: {len(TEST_CASES)}")
    print(f"Target accuracy: >95%")
    print("="*60 + "\n")
    
    results = []
    correct = 0
    total = len(TEST_CASES)
    
    for i, (complaint, expected_id, expected_level) in enumerate(TEST_CASES, 1):
        matched_id, score = match_agency(complaint)
        
        is_correct = matched_id == expected_id
        if is_correct:
            correct += 1
        
        result = {
            'case': i,
            'complaint': complaint,
            'expected': expected_id,
            'matched': matched_id,
            'score': score,
            'correct': is_correct
        }
        results.append(result)
        
        # Print result
        status = "✅" if is_correct else "❌"
        print(f"{status} Case {i:2d}: {complaint[:50]:50s} | Score: {score:.2f}")
        if not is_correct:
            print(f"          Expected: {expected_id}")
            print(f"          Got:      {matched_id}")
    
    # Calculate metrics
    accuracy = (correct / total) * 100
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"Correct:  {correct}/{total}")
    print(f"Accuracy: {accuracy:.1f}%")
    print(f"Target:   95.0%")
    print(f"Status:   {'✅ PASS' if accuracy >= 95 else '❌ FAIL'}")
    print("="*60)
    
    # Analyze failures
    failures = [r for r in results if not r['correct']]
    if failures:
        print("\n" + "="*60)
        print("FAILURE ANALYSIS")
        print("="*60)
        for f in failures:
            print(f"\nCase {f['case']}: {f['complaint']}")
            print(f"  Expected: {f['expected']}")
            print(f"  Got:      {f['matched']}")
            print(f"  Score:    {f['score']:.2f}")
    
    # Save results
    with open('matching_test_results.json', 'w') as f:
        json.dump({
            'accuracy': accuracy,
            'correct': correct,
            'total': total,
            'results': results
        }, f, indent=2)
    
    print(f"\n📁 Results saved to: matching_test_results.json")
    
    return accuracy >= 95


def analyze_diminishing_returns():
    """Analyze if we've hit diminishing returns"""
    print("\n" + "="*60)
    print("DIMINISHING RETURNS ANALYSIS")
    print("="*60)
    
    # Test with different keyword counts
    test_sizes = [10, 20, 30, 40, 50]
    accuracies = []
    
    for size in test_sizes:
        test_subset = TEST_CASES[:size]
        correct = 0
        for complaint, expected_id, _ in test_subset:
            matched_id, _ = match_agency(complaint)
            if matched_id == expected_id:
                correct += 1
        accuracy = (correct / size) * 100
        accuracies.append(accuracy)
        print(f"Test size {size:2d}: {accuracy:.1f}% accuracy")
    
    # Check if improvement is <2% for last 10 cases
    if len(accuracies) >= 2:
        improvement = accuracies[-1] - accuracies[-2]
        print(f"\nImprovement from {test_sizes[-2]} to {test_sizes[-1]}: {improvement:.1f}%")
        
        if improvement < 2:
            print("✅ Diminishing returns reached (<2% improvement)")
            return True
        else:
            print("⚠️  Still improving, could add more test cases")
            return False
    
    return False


if __name__ == '__main__':
    success = test_matching_accuracy()
    analyze_diminishing_returns()
    
    if success:
        print("\n🎉 Matching accuracy validated!")
        print("✅ Ready for production deployment")
    else:
        print("\n⚠️  Accuracy below target")
        print("🔧 Need to tune keywords or add synonyms")
