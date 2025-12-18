from starlette.testclient import TestClient as TestClient
from ..main import app
from fastapi import status

Client = TestClient(app)

def test_return_health_check():
    response = Client.get("/healthy")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'status': 'healthy'}