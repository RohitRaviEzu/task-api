from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# Tests use a throwaway in-memory SQLite database. This means "pytest" never
# needs a running Postgres server -- important later when GitHub Actions
# runs these same tests in a clean environment with no database attached.
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_get_task():
    response = client.post("/tasks", json={"title": "Write course notes"})
    assert response.status_code == 201
    task_id = response.json()["id"]

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Write course notes"


def test_update_task():
    response = client.post("/tasks", json={"title": "Draft"})
    task_id = response.json()["id"]

    response = client.put(f"/tasks/{task_id}", json={"completed": True})
    assert response.status_code == 200
    assert response.json()["completed"] is True


def test_delete_task():
    response = client.post("/tasks", json={"title": "Temp task"})
    task_id = response.json()["id"]

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 404


def test_get_missing_task_returns_404():
    response = client.get("/tasks/999999")
    assert response.status_code == 404
