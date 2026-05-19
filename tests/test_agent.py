import pytest
from app.agent.recommender import AssessmentRecommenderAgent
from app.agent.parser import extract_recommendations_from_response

def test_agent_initialization():
    """Verify that agent class can be instantiated"""
    agent = AssessmentRecommenderAgent()
    assert agent is not None

def test_out_of_scope_blocks():
    """Verify that off-topic keywords (legal, compliance, salary) are blocked"""
    agent = AssessmentRecommenderAgent()
    
    inquiries = [
        [{"role": "user", "content": "What is the standard legal minimum wage?"}],
        [{"role": "user", "content": "I want to file a compliance lawsuit against my employer."}],
        [{"role": "user", "content": "Can you review my resume and rewrite it?"}]
    ]
    
    for messages in inquiries:
        refusal = agent.check_out_of_scope(messages)
        assert refusal is not None
        assert "only help with SHL assessment selection" in refusal

def test_recommendation_parser_structured():
    """Verify primary structured recommendations section parser"""
    raw_response = """
Here are my recommendations for the role:

RECOMMENDED ASSESSMENTS:
1. **JAVA8** (Type: K) - Excellent coding assessment
   URL: https://www.shl.com/solutions/products/java/
2. **OPQ32R** (Type: P) - Personality evaluation
   URL: https://www.shl.com/solutions/products/opq32r/

Let me know if you need any adjustments.
"""
    reply, recs = extract_recommendations_from_response(raw_response)
    
    assert len(recs) == 2
    assert recs[0]["name"] == "Java 8"
    assert recs[1]["name"] == "OPQ32r"
    assert recs[0]["url"] == "https://www.shl.com/solutions/products/java/"
    assert recs[1]["url"] == "https://www.shl.com/solutions/products/opq32r/"

def test_recommendation_parser_fallback():
    """Verify contextual mentions parser fallback if header is absent"""
    raw_response = """
I suggest we evaluate candidates using the GSA test to measure verbal reasoning skills. 
Additionally, for leadership fit, the OPQ32R would be a great recommend fit!
"""
    reply, recs = extract_recommendations_from_response(raw_response)
    
    assert len(recs) == 2
    names = [r["name"] for r in recs]
    assert "GSA" in names
    assert "OPQ32r" in names
