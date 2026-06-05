from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.services.deps import _LoginRedirect
from fastapi import Request as FastAPIRequest
from fastapi.responses import RedirectResponse
from app.config import get_settings
from app.database import engine, Base

# Import models BEFORE create_all so SQLAlchemy registers all tables
from app.models import User, Book, Borrow  # noqa: F401

from app.api import auth, books, borrow, chat, audit

# Create all tables on startup
Base.metadata.create_all(bind=engine)

settings = get_settings()

app = FastAPI(
    title="BibliAi",
    description="Système de gestion de bibliothèque avec chatbot IA",
    version="1.0.0",
)

# Session middleware (simple cookie-based auth — no JWT)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie="biblio_session",
    max_age=60 * 60 * 8,  # 8 hours
    same_site="lax",
    https_only=False,
)

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routers
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(borrow.router)
app.include_router(chat.router)
app.include_router(audit.router)


@app.get("/")
def root():
    return RedirectResponse("/books", status_code=302)


# ── Seed default admin on first run ──────────────────────────────────────────
from app.database import SessionLocal
from app.services.auth_service import get_user_by_username, create_user
@app.on_event("startup")
def seed_admin():
    db = SessionLocal()
    try:
        if not get_user_by_username(db, "admin"):
            create_user(db, username="admin", email="admin@bibliotheque.com",
                        password="admin123", is_admin=True)
            print("Compte admin créé")
    finally:
        db.close()


@app.exception_handler(_LoginRedirect)
async def login_redirect_handler(request: FastAPIRequest, exc: _LoginRedirect):
    return exc.response

