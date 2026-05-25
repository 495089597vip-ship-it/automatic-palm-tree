from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.worker import worker as worker_module


SQLALCHEMY_DATABASE_URL = "sqlite:///./test_generation_tasks.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def setup_module():
    with engine.begin() as conn:
        conn.exec_driver_sql("DROP TABLE IF EXISTS generation_tasks")
        conn.exec_driver_sql(
            """
            CREATE TABLE generation_tasks (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              task_type VARCHAR(60) NOT NULL,
              payload TEXT NOT NULL,
              status VARCHAR(30) NOT NULL DEFAULT 'queued',
              result TEXT DEFAULT '',
              provider VARCHAR(40) DEFAULT 'mock',
              request_params TEXT DEFAULT '',
              response_payload TEXT DEFAULT '',
              cost_estimate NUMERIC(12,6) DEFAULT 0,
              error_reason TEXT DEFAULT ''
            )
            """
        )


def test_openai_task_success(monkeypatch):
    class StubAdapter:
        def __init__(self):
            pass

        def generate(self, prompt: str, size: str, quality: str):
            return {
                "request": {"prompt": prompt, "size": size, "quality": quality},
                "response": {"data": [{"url": "http://example.com/1.png"}]},
                "cost_estimate": 0.012,
            }

    monkeypatch.setattr(worker_module, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(worker_module, "OpenAIImageAdapter", StubAdapter)

    db = TestingSessionLocal()
    row = db.execute(text("""
        INSERT INTO generation_tasks(task_type,payload,status,provider,request_params)
        VALUES('image_generate','test','queued','openai','{"prompt":"p1","size":"1024x1024","quality":"standard"}')
        RETURNING id
    """)).fetchone()
    db.commit()
    db.close()

    worker_module.process_task(row[0])

    db = TestingSessionLocal()
    got = db.execute(text("SELECT status, response_payload, cost_estimate, error_reason FROM generation_tasks WHERE id=:id"), {"id": row[0]}).fetchone()
    db.close()
    assert got[0] == "done"
    assert "example.com" in got[1]
    assert float(got[2]) == 0.012
    assert got[3] == ""


def test_openai_task_failure(monkeypatch):
    class BadAdapter:
        def __init__(self):
            raise ValueError("OPENAI_API_KEY is not configured")

    monkeypatch.setattr(worker_module, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(worker_module, "OpenAIImageAdapter", BadAdapter)

    db = TestingSessionLocal()
    row = db.execute(text("""
        INSERT INTO generation_tasks(task_type,payload,status,provider,request_params)
        VALUES('image_generate','test','queued','openai','{"prompt":"p2"}')
        RETURNING id
    """)).fetchone()
    db.commit()
    db.close()

    worker_module.process_task(row[0])

    db = TestingSessionLocal()
    got = db.execute(text("SELECT status, error_reason FROM generation_tasks WHERE id=:id"), {"id": row[0]}).fetchone()
    db.close()
    assert got[0] == "failed"
    assert "OPENAI_API_KEY" in got[1]
