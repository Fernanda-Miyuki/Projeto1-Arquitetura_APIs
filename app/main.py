from fastapi import FastAPI

from .database import Base, engine
from .routers import users


Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="API de Usuários",
    description="API RESTful para gerenciamento de usuários",
    version="1.0.0"
)


app.include_router(
    users.router
)


@app.get(
    "/",
    tags=["Health Check"]
)
def root():

    return {
        "message": "API funcionando!",
        "status": "online"
    }