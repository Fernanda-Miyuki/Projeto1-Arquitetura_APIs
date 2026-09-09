from sqlalchemy.orm import Session

from . import models, schemas


def get_user(
    db: Session,
    user_id: int
):

    return (
        db.query(models.User)
        .filter(models.User.id == user_id)
        .first()
    )


def get_user_by_email(
    db: Session,
    email: str
):

    return (
        db.query(models.User)
        .filter(models.User.email == email)
        .first()
    )


def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 100
):

    return (
        db.query(models.User)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_user(
    db: Session,
    user: schemas.UserCreate,
    password_hash: str
):

    db_user = models.User(
        name=user.name,
        email=user.email,
        password_hash=password_hash
    )

    db.add(db_user)

    db.commit()

    db.refresh(db_user)

    return db_user


def update_user(
    db: Session,
    db_user: models.User,
    user_data: schemas.UserUpdate,
    password_hash: str | None = None
):

    if user_data.name is not None:
        db_user.name = user_data.name

    if user_data.email is not None:
        db_user.email = user_data.email

    if user_data.is_active is not None:
        db_user.is_active = user_data.is_active

    if password_hash is not None:
        db_user.password_hash = password_hash

    db.commit()

    db.refresh(db_user)

    return db_user


def delete_user(
    db: Session,
    db_user: models.User
):

    db.delete(db_user)

    db.commit()