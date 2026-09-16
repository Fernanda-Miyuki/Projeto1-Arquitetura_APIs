import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture
def client():

    Base.metadata.create_all(bind=engine)

    def override_get_db():

        db = TestingSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

    Base.metadata.drop_all(bind=engine)