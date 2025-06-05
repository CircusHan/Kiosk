import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

sys.path.append(str(Path(__file__).resolve().parents[1]))
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"


def test_reception_departments():
    res = client.get("/api/reception/departments")
    assert res.status_code == 200
    departments = res.json()
    assert isinstance(departments, list)
    assert departments
