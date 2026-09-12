from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# StaticPool forces every connection request to reuse the same single
# underlying SQLite connection, regardless of which thread asks for it.
# Without this, FastAPI's thread-pooled request handling and this test's
# setup code end up talking to two different, empty in-memory databases.
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
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
    assert response.status_code == 999
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
