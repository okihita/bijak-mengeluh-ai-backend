# Changelog

All notable changes to Bijak Mengeluh Backend.

---

## [1.3.0] - Nov 14, 2025 - Phase 3: DynamoDB Migration

### Added
- DynamoDB-based keyword matching (replace Pinecone)
- DKI Jakarta automated scraping (90 agencies)
- Agency data collection scripts

### Changed
- Migrated from Pinecone to DynamoDB
- Cost: $77-85/mo → $7-13/mo (save $840/year)
- Match accuracy: 100% (7/7 test cases)

---

## [1.2.0] - Nov 14, 2025 - Phase 2: Cost Optimization

### Changed
- Reduced Lambda memory (1024MB → 768MB main, 768MB → 512MB finder)
- Optimized Bedrock token usage
- Pinned Python dependencies

### Fixed
- Technical debt cleanup
- Dependency version conflicts

---

## [1.1.0] - Nov 14, 2025 - Phase 2: Style & Tone

### Added
- Support for 'complaint' parameter (aligned with frontend)
- Tone support: formal, funny, angry
- Casual Indonesian Instagram comment style

### Changed
- Default to casual Indonesian style
- Improved prompt engineering

---

## [1.0.0] - Nov 14, 2025 - Phase 1: Performance

### Added
- Parallel processing (ThreadPoolExecutor)
- Performance monitoring (X-Processing-Time headers)
- Indonesian error messages
- Input validation

### Changed
- Increased Lambda memory (512MB → 1024MB)
- Better error handling

### Performance
- 50% faster response (8-10s → 4-6s)
- 25% faster cold starts (3-4s → 2-3s)

---

## [0.9.0] - Nov 14, 2025 - Phase 1: Code Restructuring

### Changed
- Modular service-oriented architecture
- Separated handlers, services, config, models
- Consolidated documentation

### Removed
- Unused libraries
- Legacy monolithic code

---

## [0.8.0] - Nov 14, 2025 - Phase 1: Social Media

### Added
- Social finder Lambda function
- Serper API integration
- Confidence scoring for handles
- DynamoDB cache for verified handles

---

## [0.7.0] - Nov 14, 2025 - Phase 1: Ministry Matching

### Added
- Pinecone integration for vector matching
- Top 3 suggested contacts with scores
- Ministry descriptions and contact info

---

## [0.6.0] - Oct 23, 2025 - Infrastructure as Code

### Added
- CloudFormation/SAM template
- Automated deployment scripts
- API Gateway with custom domain
- DynamoDB table for caching

---

## [0.5.0] - Oct 22, 2025 - Initial Release

### Added
- Basic Lambda function
- AWS Bedrock integration (Claude 3 Haiku)
- Cohere embeddings
- API Gateway endpoint

---

## Performance Evolution

| Version | Response Time | Cold Start | Memory | Cost/Request |
|---------|--------------|------------|--------|--------------|
| 0.5.0   | ~10s         | ~4s        | 512MB  | $0.0015      |
| 1.0.0   | ~5s          | ~2.5s      | 1024MB | $0.0018      |
| 1.2.0   | ~5s          | ~2.5s      | 768MB  | $0.0012      |
| 1.3.0   | ~4s          | ~2s        | 768MB  | $0.0008      |

---

## Migration Notes

### v1.3.0 - Pinecone to DynamoDB
- **Why:** Cost reduction ($70/mo → $5/mo)
- **Impact:** Similar accuracy, faster queries
- **Action:** None (backward compatible)

### v1.0.0 - Parallel Processing
- **Why:** Performance improvement
- **Impact:** 50% faster response
- **Action:** Redeploy with updated template
