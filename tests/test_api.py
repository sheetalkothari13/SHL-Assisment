from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    """Verify health endpoint returns ok status"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_catalog_endpoint():
    """Verify full catalog retrieval"""
    response = client.get("/catalog")
    assert response.status_code == 200
    catalog = response.json()
    assert "K" in catalog
    assert "P" in catalog
    assert "A" in catalog
    assert "I" in catalog

def test_catalog_search_endpoint():
    """Verify catalog query routing"""
    response = client.get("/catalog/search?q=python")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["code"] == "PYTHON"

def test_sessions_crud():
    """Verify complete stateful Session database lifecycle (Create -> List -> Get -> Delete)"""
    # 1. Create a persistent session
    response = client.post("/sessions")
    assert response.status_code == 200
    session = response.json()
    assert "id" in session
    assert session["title"] == "New Assessment Campaign"
    assert session["turn_count"] == 0
    
    session_id = session["id"]
    
    # 2. List all sessions from DB
    list_response = client.get("/sessions")
    assert list_response.status_code == 200
    sessions_list = list_response.json()
    assert any(s["id"] == session_id for s in sessions_list)
    
    # 3. Retrieve session with initial welcome message
    get_response = client.get(f"/sessions/{session_id}")
    assert get_response.status_code == 200
    details = get_response.json()
    assert details["id"] == session_id
    assert len(details["messages"]) == 1
    assert details["messages"][0]["role"] == "assistant"
    assert "SHL Assessment Advisor" in details["messages"][0]["content"]
    
    # 4. Delete session from SQLite
    delete_response = client.delete(f"/sessions/{session_id}")
    assert delete_response.status_code == 200
    
    # 5. Confirm deletion
    get_confirm = client.get(f"/sessions/{session_id}")
    assert get_confirm.status_code == 404
