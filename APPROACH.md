# SHL Assessment Recommender - Approach Document

## Problem Decomposition

The task decomposes into four critical components:

1. **Catalog Organization**: Structure SHL assessments to enable semantic search and filtering
2. **Conversational Agent**: Build dialogue logic that clarifies, recommends, refines, and compares
3. **API Service**: Expose stateless endpoints with strict schema compliance
4. **Scope Management**: Enforce boundaries on what the agent discusses

## Design Choices

### 1. Catalog Structure
- **Approach**: Hierarchical catalog organized by assessment type (Knowledge, Personality, Ability, Industry-Specific)
- **Why**: Enables filtering by type while maintaining full semantic information for each assessment
- **Tradeoff**: Manual curation of 20+ assessments vs. automated scraping. Chose curation for reliability since scraped data may be fragile

**Catalog Schema**:
```python
{
  "type": "K/P/A/I",
  "name": "Assessment Name",
  "code": "CODE",
  "url": "https://...",
  "description": "...",
  "skills": [...],  # For knowledge tests
  "dimensions": [...],  # For personality tests
  "use_cases": [...]  # For all types
}
```

### 2. Agent Design

**Behavior State Machine**:
- **Turn 1-2**: CLARIFY mode. If query is vague, ask targeted questions about role, seniority, competencies
- **Turn 2-4**: RECOMMEND mode. Once context is sufficient, provide 1-10 assessments with explanations
- **Turn 3+**: REFINE mode. If user changes constraints, update recommendations without restarting
- **Anytime**: COMPARE mode. If user asks "What's difference between X and Y?", answer from catalog data

**Implementation**: Used Claude 3.5 Sonnet with explicit instructions for each behavior in system prompt. The prompt:
- Shows catalog structure with all assessments
- Defines clear decision points (e.g., "Do NOT recommend on turn 1 if vague")
- Specifies output format with `RECOMMENDED ASSESSMENTS:` section for easy parsing
- Lists scope boundaries explicitly

**Why Sonnet**: 
- Fast enough for 30s timeout with reasonable context
- Instruction-following is reliable for scope boundaries
- Can handle conversation history effectively

### 3. Recommendation Extraction

**Challenge**: Claude's natural language responses don't always match a fixed format. Solution: Two-pass extraction

1. **Structured Pass**: Look for `RECOMMENDED ASSESSMENTS:` section with `**CODE**` patterns
2. **Fallback Pass**: If structured section absent, search for assessment codes with recommendation context
3. **Validation**: Verify all URLs come from catalog, limit to 10 recommendations

**Why This Works**: 
- Survives variations in Claude's output
- Doesn't break on recommendations embedded in prose
- Catches most recommendation patterns

### 4. Scope Enforcement

**Approach**: Three-layer defense:
1. **Request-level**: Check for off-topic keywords before calling Claude ("legal", "salary", "hire me")
2. **Prompt-level**: System prompt explicitly forbids off-topic answers
3. **Response-level**: Before returning, validate all URLs are in catalog

**Keywords Monitored**: legal, lawsuit, compliance, hire, resume, interview, salary, benefits

## Context Engineering

The system prompt teaches Claude to:
- **Ask before recommending**: Pattern recognition from input clarifies when more info is needed
- **Use catalog as ground truth**: Exact assessment details prevent hallucinations
- **Maintain conversation context**: Each turn builds on prior messages to refine recommendations
- **Format for parsing**: `RECOMMENDED ASSESSMENTS:` section enables extraction

The 1000-token max output keeps responses focused while allowing 1-2 recommendations per turn.

## What Didn't Work & Iterations

1. **Naive regex extraction**: First tried regex for `**CODE**` patterns. Failed on variations. Added fallback logic.
2. **Turn-based state**: Initially tracked state on client. Switched to stateless API as required—state is implicit in conversation history.
3. **Keyword-only search**: Initially filtered by keywords alone. Added semantic understanding via Claude for better matching.
4. **Vague turn 1 recommendations**: Claude initially recommended even with vague input. Fixed by adding explicit "Do NOT recommend" instruction.

## Evaluation Approach

### Automated Testing
- **Schema Compliance**: Validate response format (reply, recommendations, end_of_conversation)
- **Timeout**: Ensure responses complete in <30s
- **Scope**: Verify all URLs from catalog, reject off-topic queries
- **Turn Limit**: Enforce 8-turn maximum

### Manual Testing
- **Clarification**: Verify agent asks questions before recommending on vague inputs
- **Recommendation Quality**: Check recommendations match the stated job requirements
- **Refinement**: Test that "add X test type" updates the shortlist
- **Comparison**: Ask "What's the difference?" and verify answer comes from catalog data
- **Out-of-Scope**: Confirm agent refuses legal/hiring advice questions

### Recall@K Evaluation
- **Definition**: For each conversation, measure % of relevant assessments in top 10
- **Methodology**: Compare agent's shortlist to ground truth labels for test cases
- **Target**: Mean Recall@10 >= 0.75 across public and holdout test sets

## Stack Justification

| Component | Choice | Why |
|-----------|--------|-----|
| LLM | Claude 3.5 Sonnet | Instruction-following, cost-effective, 30s latency acceptable |
| Framework | FastAPI | Simple, fast, built-in schema validation |
| Catalog | Python dict | No external dependencies, easy to version control |
| Deployment | Docker/Render | Stateless allows horizontal scaling, easy CI/CD |
| Testing | pytest | Simple, captures core behaviors |
| Frontend | Glassmorphism SPA | Beautiful, vanilla CSS and JS, live Catalog Browser |

## Known Limitations & Future Work

1. **Catalog Completeness**: Manually curated 20+ assessments. Full SHL catalog has 100+. Real version would auto-sync.
2. **No Learning**: System doesn't improve from user feedback. Would add rating system for production.
3. **No Conversation History Search**: Can't reference "the assessment we discussed earlier." Would require context search.
4. **Basic Comparison**: Comparison relies on catalog fields. Could enhance with LLM-generated summaries.

## Deployment

**Render/Railway**:
```bash
git push heroku main  # or equivalent for your platform
# Service automatically builds from Dockerfile
# Environment: set ANTHROPIC_API_KEY
```

**Local Testing**:
```bash
pip install -r requirements.txt
python -m pytest test_agent.py -v
python main.py  # runs on localhost:8000
```

## API Contract

```
GET /health -> {"status": "ok"}

POST /chat
{
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
Response:
{
  "reply": "...",
  "recommendations": [
    {"name": "...", "url": "...", "test_type": "K"}
  ],
  "end_of_conversation": false
}
```
