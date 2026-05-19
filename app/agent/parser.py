from typing import List, Dict, Tuple
from app.catalog.database import get_all_assessments

def extract_recommendations_from_response(response_text: str) -> Tuple[str, List[Dict]]:
    """
    Extract text response and structured recommendations from the agent's text response.
    Uses a robust two-pass strategy (Structured header section -> Contextual mentions fallback).
    """
    catalog = get_all_assessments()
    recommendations = []
    
    # Strategy 1: Look for "RECOMMENDED ASSESSMENTS:" section
    if "RECOMMENDED ASSESSMENTS:" in response_text:
        # Extract the recommendations section
        start_idx = response_text.find("RECOMMENDED ASSESSMENTS:")
        recommendations_section = response_text[start_idx:]
        
        # Parse lines looking for assessment codes
        lines = recommendations_section.split('\n')
        for line in lines:
            # Look for pattern: **CODE** or 1. **CODE**
            for assessment in catalog:
                code = assessment.get("code", "")
                name = assessment.get("name", "")
                url = assessment.get("url", "")
                test_type = assessment.get("type", "")
                
                if f"**{code}**" in line or f"**{name}**" in line:
                    # Verify this isn't a duplicate
                    if not any(r["name"] == name for r in recommendations):
                        recommendations.append({
                            "name": name,
                            "url": url,
                            "test_type": test_type
                        })
        
    # Strategy 2: If no structured section, look for mentions with high confidence
    if not recommendations:
        # Look for assessment codes mentioned in context suggesting recommendation
        for assessment in catalog:
            code = assessment.get("code", "")
            name = assessment.get("name", "")
            url = assessment.get("url", "")
            test_type = assessment.get("type", "")
            
            # Check if code appears with recommendation language
            if code in response_text:
                # Look in surrounding context
                context_keywords = ["recommend", "suggest", "assess", "evaluate", "good fit", "suitable", "shortlist"]
                if any(keyword in response_text.lower() for keyword in context_keywords):
                    # High confidence this is a recommendation
                    if code in response_text.upper():  # Code appears in uppercase
                        recommendations.append({
                            "name": name,
                            "url": url,
                            "test_type": test_type
                        })
        
    # Remove duplicates while preserving order
    seen = set()
    unique_recommendations = []
    for rec in recommendations:
        if rec["name"] not in seen:
            seen.add(rec["name"])
            unique_recommendations.append(rec)
        
    # Limit to top 10
    recommendations = unique_recommendations[:10]
    
    return response_text, recommendations
