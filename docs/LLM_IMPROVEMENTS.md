# LLM Improvements

Planned improvements for AI/LLM usage in Bijak Mengeluh Backend.

---

## Current LLM Usage

### Models
- **Cohere Embed Multilingual v3** - Text embeddings
- **Claude 3 Haiku** - Text generation (complaints, rationale, handle extraction)

### Use Cases
1. **Complaint Generation** - Convert informal to formal text
2. **Rationale Generation** - Explain ministry selection
3. **Handle Extraction** - Extract social media handles from search results

---

## Improvement Opportunities

### 1. Enhanced Prompts
**Priority:** HIGH  
**Impact:** Better quality outputs

- Add explicit tone and formality specifications
- Include structure requirements (greeting, issue, request, closing)
- Add length constraints (150-300 words)
- Emphasize formal Indonesian (Bahasa Indonesia baku)

### 2. Few-Shot Learning
**Priority:** MEDIUM  
**Impact:** More consistent results

- Add 2-3 examples for rationale generation
- Include edge cases (low confidence matches)
- Provide fallback templates

### 3. Structured Output
**Priority:** HIGH  
**Impact:** More reliable parsing

- Use Claude's JSON mode for handle extraction
- Add validation rules
- Implement retry with clarification
- Add confidence scoring

### 4. Temperature Tuning
**Priority:** MEDIUM  
**Impact:** Better output quality

- **Complaint Generation:** temperature=0.7 (creative but consistent)
- **Rationale Generation:** temperature=0.3 (factual)
- **Handle Extraction:** temperature=0.0 (strict)

### 5. Context Optimization
**Priority:** MEDIUM  
**Impact:** 25% cost reduction

- Truncate ministry descriptions to 200 chars
- Limit search results to top 3
- Remove redundant instructions
- Use prompt caching

### 6. Prompt Injection Protection
**Priority:** HIGH  
**Impact:** Security

- Sanitize user input
- Add input length limits (max 500 chars)
- Use XML tags to separate user content
- Detect injection attempts

### 7. Error Handling
**Priority:** HIGH  
**Impact:** Better reliability

- Retry failed LLM calls with exponential backoff
- Fallback to simpler prompts on timeout
- Return partial results if some calls fail
- Circuit breaker for Bedrock outages

### 8. Caching
**Priority:** MEDIUM  
**Impact:** 40% cost reduction

- Cache embeddings for common phrases
- Cache rationale for frequent ministries
- Use semantic similarity for cached results

---

## Implementation Priority

### Phase 1 (Immediate)
1. Enhanced complaint generation prompt
2. Structured output for handle extraction
3. Prompt injection protection

### Phase 2 (Short-term)
4. Few-shot rationale generation
5. Temperature tuning
6. Context optimization

### Phase 3 (Medium-term)
7. Error handling & fallbacks
8. Caching layer

---

## Success Metrics

- **Quality:** User satisfaction > 4.5/5
- **Reliability:** Success rate > 99%
- **Cost:** Token usage -25%
- **Speed:** Response time < 3s
- **Accuracy:** Ministry match > 90%

---

## Estimated Impact

| Improvement | Cost Reduction | Quality Gain | Effort |
|-------------|----------------|--------------|--------|
| Enhanced prompts | 10% | High | Low |
| Structured output | 5% | High | Low |
| Context optimization | 25% | Medium | Medium |
| Caching | 40% | None | High |
| Temperature tuning | 0% | Medium | Low |

**Total Potential:** 50-60% cost reduction, significant quality improvement
