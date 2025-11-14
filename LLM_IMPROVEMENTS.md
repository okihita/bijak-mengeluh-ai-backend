# LLM Improvements Specification

## Current LLM Usage Analysis

### Models in Use
1. **Cohere Embed Multilingual v3** - Text embeddings
2. **Claude 3 Haiku** - Text generation (complaints, rationale, handle extraction)

### Current Prompts

#### 1. Complaint Generation
- **Purpose**: Convert informal complaint to formal text
- **Issues**:
  - No tone specification (formal level unclear)
  - No length guidance
  - No structure requirements
  - Missing Indonesian language emphasis

#### 2. Rationale Generation
- **Purpose**: Explain ministry selection
- **Issues**:
  - Good example provided
  - Could benefit from few-shot examples
  - No fallback for low-confidence matches

#### 3. Handle Extraction
- **Purpose**: Extract Twitter handle from search results
- **Issues**:
  - Relies on JSON parsing (fragile)
  - No retry mechanism for malformed responses
  - Could use structured output

---

## Proposed Improvements

### 1. Enhanced Complaint Generation Prompt

**Priority**: HIGH  
**Impact**: Better user experience, more professional outputs

**Improvements**:
- Add explicit tone and formality level
- Specify structure (greeting, issue, request, closing)
- Add length constraints (150-300 words)
- Emphasize Indonesian formal language (Bahasa Indonesia baku)
- Include formatting guidelines

**Example Enhancement**:
```
You are an expert in writing formal Indonesian government complaints.

Write a professional complaint letter in Bahasa Indonesia with:
- Formal greeting (Kepada Yth.)
- Clear problem statement
- Specific details from user input
- Polite request for action
- Professional closing

Length: 150-300 words
Tone: Respectful, assertive, professional
Language: Bahasa Indonesia baku (formal Indonesian)
```

---

### 2. Few-Shot Rationale Generation

**Priority**: MEDIUM  
**Impact**: More consistent, higher quality explanations

**Improvements**:
- Add 2-3 few-shot examples
- Include edge cases (low confidence matches)
- Add fallback rationale template

**Example Enhancement**:
```
Here are examples of good rationales:

Example 1:
Complaint: "Jalan di depan rumah rusak parah"
Ministry: Kementerian PUPR
Rationale: "Kementerian PUPR bertanggung jawab atas infrastruktur jalan..."

Example 2:
[Add more examples]

Now generate rationale for:
[Current complaint and ministry]
```

---

### 3. Structured Output for Handle Extraction

**Priority**: HIGH  
**Impact**: More reliable parsing, fewer errors

**Improvements**:
- Use Claude's JSON mode or structured output
- Add validation rules
- Implement retry with clarification
- Add confidence scoring explanation

**Example Enhancement**:
```
Respond ONLY with valid JSON. No additional text.

Required format:
{
  "handle": "@example" or "NOT_FOUND",
  "confidence": "high" | "medium" | "low" | "none",
  "reasoning": "Brief explanation of confidence level"
}

Validation rules:
- handle must start with @ or be "NOT_FOUND"
- confidence must be one of the four levels
- reasoning must be 1 sentence
```

---

### 4. Prompt Versioning & A/B Testing

**Priority**: LOW  
**Impact**: Long-term optimization

**Implementation**:
- Add version numbers to prompts
- Log prompt version with each request
- Enable A/B testing different prompt variations
- Track metrics (user satisfaction, accuracy)

---

### 5. Context Window Optimization

**Priority**: MEDIUM  
**Impact**: Cost reduction, faster responses

**Current Issues**:
- Full ministry descriptions sent to LLM
- Search results not truncated
- Redundant context in prompts

**Improvements**:
- Truncate ministry descriptions to 200 chars
- Limit search results to top 3 (currently 5)
- Remove redundant instructions
- Use prompt caching for repeated elements

**Estimated Savings**: 20-30% token reduction

---

### 6. Multi-Language Support

**Priority**: LOW  
**Impact**: Broader accessibility

**Improvements**:
- Detect input language
- Generate complaint in user's language
- Support English, Indonesian, regional languages
- Add language parameter to API

---

### 7. Temperature & Parameter Tuning

**Priority**: MEDIUM  
**Impact**: Better output quality

**Current**: Using default parameters

**Recommendations**:
- **Complaint Generation**: temperature=0.7 (creative but consistent)
- **Rationale Generation**: temperature=0.3 (factual, deterministic)
- **Handle Extraction**: temperature=0.0 (strict, no creativity)
- Add max_tokens limits per use case

---

### 8. Fallback & Error Handling

**Priority**: HIGH  
**Impact**: Better reliability

**Improvements**:
- Retry failed LLM calls with exponential backoff
- Fallback to simpler prompts on timeout
- Return partial results if some LLM calls fail
- Add circuit breaker for Bedrock outages

---

### 9. Prompt Injection Protection

**Priority**: HIGH  
**Impact**: Security

**Current Risk**: User input directly inserted into prompts

**Improvements**:
- Sanitize user input
- Add input length limits (max 500 chars)
- Detect and block prompt injection attempts
- Use XML tags to separate user content from instructions

**Example**:
```
<user_input>
{sanitized_user_prompt}
</user_input>

Generate complaint based on the user input above.
```

---

### 10. Caching & Deduplication

**Priority**: MEDIUM  
**Impact**: Cost savings

**Improvements**:
- Cache embeddings for common phrases
- Deduplicate similar complaints
- Cache rationale for frequently matched ministries
- Use semantic similarity to return cached results

---

## Implementation Priority

### Phase 1 (Immediate - Week 1)
1. ✅ Enhanced complaint generation prompt
2. ✅ Structured output for handle extraction
3. ✅ Prompt injection protection

### Phase 2 (Short-term - Week 2-3)
4. Few-shot rationale generation
5. Temperature & parameter tuning
6. Context window optimization

### Phase 3 (Medium-term - Month 2)
7. Fallback & error handling
8. Prompt versioning
9. Caching & deduplication

### Phase 4 (Long-term - Month 3+)
10. Multi-language support
11. A/B testing framework

---

## Success Metrics

- **Quality**: User satisfaction score (target: >4.5/5)
- **Reliability**: Success rate (target: >99%)
- **Cost**: Token usage per request (target: -25%)
- **Speed**: Average response time (target: <3s)
- **Accuracy**: Ministry match relevance (target: >90%)

---

## Estimated Impact

| Improvement | Cost Reduction | Quality Gain | Effort |
|-------------|----------------|--------------|--------|
| Enhanced prompts | 10% | High | Low |
| Structured output | 5% | High | Low |
| Context optimization | 25% | Medium | Medium |
| Caching | 40% | None | High |
| Temperature tuning | 0% | Medium | Low |
| Fallback handling | 0% | High | Medium |

**Total Potential**: 50-60% cost reduction, significant quality improvement
