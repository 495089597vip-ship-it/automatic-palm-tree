from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_shots.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def setup_module():
    with engine.begin() as conn:
        conn.exec_driver_sql("DROP TABLE IF EXISTS shots")
        conn.exec_driver_sql(
            """
            CREATE TABLE shots (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              episode INTEGER NOT NULL,
              scene_no VARCHAR(50) NOT NULL,
              shot_no VARCHAR(50) NOT NULL,
              duration_sec INTEGER NOT NULL,
              aspect_ratio VARCHAR(30) NOT NULL,
              shot_size VARCHAR(30) NOT NULL,
              camera_angle VARCHAR(30) NOT NULL,
              action TEXT DEFAULT '',
              dialogue TEXT DEFAULT '',
              visual_requirements TEXT DEFAULT '',
              negative_prompt TEXT DEFAULT '',
              status VARCHAR(30) DEFAULT 'draft'
            )
            """
        )


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_shot_crud():
    payload = {
        "episode": 1,
        "scene_no": "A1",
        "shot_no": "001",
        "duration_sec": 6,
        "aspect_ratio": "16:9",
        "shot_size": "近景",
        "camera_angle": "平视",
        "action": "角色走入画面",
        "dialogue": "你好",
        "visual_requirements": "暖色调",
        "negative_prompt": "模糊",
        "status": "draft"
    }

    res = client.post('/api/shots', json=payload)
    assert res.status_code == 200
    shot_id = res.json()['id']

    list_res = client.get('/api/shots')
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    upd = client.put(f'/api/shots/{shot_id}', json={"status": "done", "duration_sec": 8})
    assert upd.status_code == 200

    got = client.get('/api/shots').json()[0]
    assert got['status'] == 'done'
    assert got['duration_sec'] == 8

    delete_res = client.delete(f'/api/shots/{shot_id}')
    assert delete_res.status_code == 200
