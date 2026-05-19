from typing import List, Dict
from app.catalog.data import SHL_CATALOG

def get_all_assessments() -> List[Dict]:
    """Flatten catalog into a list of all assessments"""
    all_assessments = []
    for category, data in SHL_CATALOG.items():
        all_assessments.extend(data["assessments"])
    return all_assessments

def search_assessments(query: str) -> List[Dict]:
    """Search assessments by name, description, or skills"""
    query_lower = query.lower()
    results = []
    
    for assessment in get_all_assessments():
        # Search in name
        if query_lower in assessment.get("name", "").lower():
            results.append(assessment)
            continue
        
        # Search in description
        if query_lower in assessment.get("description", "").lower():
            results.append(assessment)
            continue
        
        # Search in skills/roles
        for field in ["skills", "roles", "dimensions", "subtests", "use_cases"]:
            if any(query_lower in item.lower() for item in assessment.get(field, [])):
                results.append(assessment)
                break
    
    return results

def get_assessment_by_code(code: str) -> Dict:
    """Get single assessment by code"""
    for assessment in get_all_assessments():
        if assessment.get("code") == code:
            return assessment
    return None
