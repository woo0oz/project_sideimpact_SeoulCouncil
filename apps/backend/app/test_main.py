from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)

def test_get_districts():
    response = client.get("/api/v1/districts")
    assert response.status_code == 200

def test_get_categories():
    response = client.get("/api/v1/categories")
    assert response.status_code == 200