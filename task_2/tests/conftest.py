import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.storage import clear_all

@pytest.fixture
def client():
    clear_all()
    
    with TestClient(app) as test_client:
        yield test_client
        
    clear_all()