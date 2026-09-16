from app import crud, models, schemas
from app.database import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Banco SQLite exclusivo para o teste
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base.metadata.create_all(bind=engine)


def test_create_user():
    db = TestingSessionLocal()

    user_data = schemas.UserCreate(
        name="Usuário Teste",
        email="teste@teste.com",
        password="12345678"
    )

    user = crud.create_user(
        db,
        user_data,
        "hash_da_senha"
    )

    assert user.id is not None
    assert user.name == "Usuário Teste"
    assert user.email == "teste@teste.com"

    db.close()


def test_get_user():
    db = TestingSessionLocal()

    user_data = schemas.UserCreate(
        name="Maria",
        email="maria@teste.com",
        password="12345678"
    )

    created_user = crud.create_user(
        db,
        user_data,
        "hash_da_senha"
    )

    user = crud.get_user(
        db,
        created_user.id
    )

    assert user is not None
    assert user.email == "maria@teste.com"

    db.close()