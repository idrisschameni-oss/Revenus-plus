from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, engine
from . import models
from .routers import admin, auth, expenses, referral, salary, transactions

# Crée les tables si elles n'existent pas encore. Pour de vraies migrations
# en production (modifications de schéma ultérieures), utiliser Alembic
# plutôt que de dépendre uniquement de create_all.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Revenus+ API",
    description="API pour l'application de gestion de revenus, dépenses et transactions.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(referral.router)
app.include_router(salary.router)
app.include_router(expenses.router)
app.include_router(transactions.router)
app.include_router(admin.router)


@app.middleware("http")
async def activity_logging_middleware(request: Request, call_next):
    response = await call_next(request)
    # Log request metadata only; never store passwords, tokens, or request bodies.
    if request.url.path.startswith("/api/") and request.url.path != "/api/health":
        user_id = None
        auth_header = request.headers.get("authorization", "")
        if auth_header.lower().startswith("bearer "):
            try:
                import jwt
                payload = jwt.decode(auth_header.split(" ", 1)[1], settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                user_id = int(payload.get("sub")) if payload.get("sub") else None
            except Exception:
                user_id = None
        try:
            db = Session(bind=engine)
            db.add(models.ActivityLog(user_id=user_id, method=request.method, path=request.url.path, status_code=response.status_code))
            db.commit()
            db.close()
        except Exception:
            pass
    return response


@app.get("/api/health", tags=["health"])
def health():
    return {"status": "ok"}
