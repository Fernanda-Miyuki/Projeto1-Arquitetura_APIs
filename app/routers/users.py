from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)

from pwdlib import PasswordHash

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


password_hash = PasswordHash.recommended()


@router.post(
    "/",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):


    existing_user = crud.get_user_by_email(
        db,
        user.email
    )

    if existing_user:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um usuário com este e-mail."
        )


    hashed_password = password_hash.hash(
        user.password
    )

    try:

        return crud.create_user(
            db,
            user,
            hashed_password
        )

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail já cadastrado."
        )


@router.get(
    "/",
    response_model=list[schemas.UserResponse],
    status_code=status.HTTP_200_OK
)
def list_users(
    skip: int = Query(
        default=0,
        ge=0
    ),

    limit: int = Query(
        default=100,
        ge=1,
        le=100
    ),

    db: Session = Depends(get_db)
):

    return crud.get_users(
        db,
        skip=skip,
        limit=limit
    )




@router.get(
    "/{user_id}",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_200_OK
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):

    user = crud.get_user(
        db,
        user_id
    )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )

    return user




@router.put(
    "/{user_id}",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_200_OK
)
def update_user(
    user_id: int,
    user_data: schemas.UserUpdate,
    db: Session = Depends(get_db)
):


    user = crud.get_user(
        db,
        user_id
    )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )

    if user_data.email is not None:

        existing_user = crud.get_user_by_email(
            db,
            user_data.email
        )

        if (
            existing_user
            and existing_user.id != user_id
        ):

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este e-mail já está sendo utilizado."
            )

    hashed_password = None


    if user_data.password is not None:

        hashed_password = password_hash.hash(
            user_data.password
        )

    try:

        return crud.update_user(
            db,
            user,
            user_data,
            hashed_password
        )

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não foi possível atualizar o usuário."
        )




@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):

    user = crud.get_user(
        db,
        user_id
    )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )


    crud.delete_user(
        db,
        user
    )

    return None