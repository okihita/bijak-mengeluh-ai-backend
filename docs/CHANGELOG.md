# Changelog

All notable changes to the Bijak Mengeluh Backend project.

---

## [1.3.0] - 2025-11-14 - DynamoDB Matching

### Added
- DynamoDB-based ministry matching for production
- DKI Jakarta automated scraping implementation
- Agency data collection scripts

### Changed
- Migrated from Pinecone to DynamoDB for cost optimization
- Improved scraping reliability with monitoring

---

## [1.2.0] - 2025-11-14 - Cost Optimization

### Changed
- Reduced Lambda memory allocation (1024MB → 768MB main, 768MB → 512MB finder)
- Optimized Bedrock token usage
- Pinned Python dependencies for reproducible builds

### Fixed
- Technical debt cleanup
- Dependency version conflicts

---

## [1.1.0] - 2025-11-14 - Style & Tone Support

### Added
- Support for 'complaint' parameter (aligned with frontend)
- Tone support: formal, funny, angry
- Casual Indonesian Instagram comment style

### Changed
- Default complaint style to casual Indonesian
- Improved prompt engineering for better tone control

---

## [1.0.0] - 2025-11-14 - Phase 1 Release

### Added
- **Parallel processing** using ThreadPoolExecutor
- **Performance monitoring** with X-Processing-Time headers
- **Indonesian error messages** for better UX
- **Input validation** on server side

### Changed
- Increased Lambda memory (512MB → 1024MB main, 512MB → 768MB finder)
- Improved logging with performance metrics
- Better error handling with proper HTTP status codes

### Performance
- 50% faster response times (8-10s → 4-6s)
- 25% faster cold starts (3-4s → 2-3s)
- Parallel operations save 3-4 seconds per request

---

## [0.9.0] - 2025-11-14 - Code Restructuring

### Changed
- Restructured code into modular service-oriented architecture
- Separated handlers, services, config, and models
- Removed old monolithic files
- Consolidated and improved documentation

### Removed
- Unused libraries from requirements.txt
- Legacy monolithic code files

---

## [0.8.0] - 2025-11-14 - Social Media Integration

### Added
- Social finder Lambda function
- Serper API integration for social media handle lookup
- Confidence scoring for social media handles
- DynamoDB cache for verified handles

### Changed
- Enhanced Lambda timeout for better performance
- Updated SAM template with Serper API key parameter

---

## [0.7.0] - 2025-11-14 - Ministry Matching

### Added
- Pinecone integration for vector-based ministry matching
- Top 3 suggested contacts with relevance scores
- Ministry descriptions and contact information

### Changed
- Improved complaint generation with ministry context

---

## [0.6.0] - 2025-10-23 - Infrastructure as Code

### Added
- CloudFormation/SAM template for infrastructure
- Automated deployment scripts
- API Gateway with custom domain
- DynamoDB table for caching

### Changed
- Migrated from manual setup to IaaC
- Standardized deployment process

---

## [0.5.0] - 2025-10-22 - Initial Release

### Added
- Basic Lambda function for complaint generation
- AWS Bedrock integration (Claude 3 Haiku)
- Cohere embeddings for text processing
- API Gateway endpoint
- Basic error handling

---

## Key Metrics Over Time

| Version | Response Time | Cold Start | Memory | Cost/Request |
|---------|--------------|------------|--------|--------------|
| 0.5.0   | ~10s         | ~4s        | 512MB  | $0.0015      |
| 1.0.0   | ~5s          | ~2.5s      | 1024MB | $0.0018      |
| 1.2.0   | ~5s          | ~2.5s      | 768MB  | $0.0012      |
| 1.3.0   | ~4s          | ~2s        | 768MB  | $0.0008      |

---

## Migration Notes

### v1.3.0 - Pinecone to DynamoDB
- **Reason:** Cost reduction (Pinecone: $70/mo → DynamoDB: ~$5/mo)
- **Impact:** Slightly different matching algorithm, but similar accuracy
- **Action Required:** None for existing deployments

### v1.0.0 - Parallel Processing
- **Reason:** Performance improvement
- **Impact:** 50% faster response times
- **Action Required:** Redeploy with updated template

### v0.6.0 - IaaC Migration
- **Reason:** Standardize infrastructure management
- **Impact:** Easier deployments and rollbacks
- **Action Required:** Delete manual resources, deploy via SAM
