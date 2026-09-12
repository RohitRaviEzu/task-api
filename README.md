# Task Management API

A deliberately small FastAPI + PostgreSQL project used as the running example
for a hands-on deployment course. The app itself is not the point --
deployment is. See `COURSE_ROADMAP.md` for the syllabus.

## Endpoints

```
GET    /health
GET    /tasks
GET    /tasks/{id}
POST   /tasks
PUT    /tasks/{id}
DELETE /tasks/{id}
```

## Local setup (Part 1)

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

createdb taskdb                  # or create it via psql / a GUI client

cp .env.example .env
uvicorn app.main:app --reload
```

Then visit http://127.0.0.1:8000/docs for interactive API docs, or:

```bash
curl http://127.0.0.1:8000/health
```

## Tests

```bash
pytest
```

More sections (Docker, Compose, deployment, CI/CD) are added as the course
progresses.
