from fastapi import FastAPI

from .database import Base, SessionLocal, engine
from .routes.admin import router as admin_router
from .routes.auth import router as auth_router
from .routes.mock import router as mock_router
from .seed import seed_data

app = FastAPI(title="Custom Auth/AuthZ API", version="1.0.0")


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "ok"}


app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(mock_router)
