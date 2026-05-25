from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_characters.db"
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
        conn.exec_driver_sql("DROP TABLE IF EXISTS characters")
        conn.exec_driver_sql(
            """
            CREATE TABLE characters (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name VARCHAR(120) NOT NULL,
              description TEXT DEFAULT '',
              appearance TEXT DEFAULT '',
              personality TEXT DEFAULT '',
              reference_image_url TEXT DEFAULT ''
            )
            """
        )


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_characters_list_and_create():
    first_list = client.get('/api/characters')
    assert first_list.status_code == 200
    assert isinstance(first_list.json(), list)

    create_res = client.post('/api/characters', json={
        "name": "林云",
        "description": "第二血脉项目中的女神零号角色",
        "appearance": "年轻女性，冷静、理性、具有未来科技感",
        "personality": "克制、理性、具有战略意识",
        "reference_image_url": ""
    })
    assert create_res.status_code == 200
    created = create_res.json()
    assert created['name'] == '林云'

    second_list = client.get('/api/characters')
    assert second_list.status_code == 200
    data = second_list.json()
    assert any(i['name'] == '林云' for i in data)
