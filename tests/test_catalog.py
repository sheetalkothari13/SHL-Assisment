import pytest
from app.catalog.data import SHL_CATALOG
from app.catalog.database import get_all_assessments, search_assessments, get_assessment_by_code

def test_catalog_structure():
    """Verify raw catalog is properly populated and grouped"""
    assert len(SHL_CATALOG) == 4
    for key in ["K", "P", "A", "I"]:
        assert key in SHL_CATALOG
        assert "name" in SHL_CATALOG[key]
        assert "assessments" in SHL_CATALOG[key]
        assert len(SHL_CATALOG[key]["assessments"]) > 0

def test_get_all_assessments():
    """Verify catalog flattening yields all assessments"""
    assessments = get_all_assessments()
    assert len(assessments) == 20
    
    # Check required schemas on all items
    required_fields = ["name", "code", "url", "type", "domain", "description"]
    for item in assessments:
        for field in required_fields:
            assert field in item, f"Assessment {item.get('name', 'Unknown')} missing {field}"

def test_catalog_search():
    """Verify fuzzy search retrieves items by name, description, or subfields"""
    # 1. Search by name
    python_matches = search_assessments("python")
    assert len(python_matches) == 1
    assert python_matches[0]["code"] == "PYTHON"
    
    # 2. Search by skill
    aws_matches = search_assessments("cloud")
    assert len(aws_matches) == 1
    assert aws_matches[0]["code"] == "AWS"
    
    # 3. Search by subtests / dimensions
    gsa_matches = search_assessments("verbal reasoning")
    assert len(gsa_matches) == 1
    assert gsa_matches[0]["code"] == "GSA"

def test_get_by_code():
    """Verify retrieving individual tests by uppercase/lowercase code"""
    opq = get_assessment_by_code("OPQ32R")
    assert opq is not None
    assert opq["name"] == "OPQ32r"
    
    sjt = get_assessment_by_code("SJT")
    assert sjt is not None
    assert sjt["name"] == "Situational Judgment Test"
    
    # Invalid code
    assert get_assessment_by_code("INVALID_CODE") is None
