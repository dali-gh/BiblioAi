from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Book, User, Borrow
from app.services.auth_service import authenticate_user, create_user, get_user_by_username
from app.services.deps import get_optional_user
from app.services.audit_service import create_audit_log

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# ── Landing page ───────────────────────────────────────────────────────────────

@router.get("/", response_class=HTMLResponse)
def landing_page(request: Request, db: Session = Depends(get_db)):
    user = get_optional_user(request, db)
    if user:
        return RedirectResponse("/books", status_code=302)

    total_books    = db.query(func.count(Book.id)).scalar()
    total_users    = db.query(func.count(User.id)).scalar()
    total_emprunts = db.query(func.count(Borrow.id)).scalar()
    total_category = db.query(func.count(Book.categorie.distinct())).scalar()

    return templates.TemplateResponse(
        "landing.html",
        {
            "request":        request,
            "total_books":    total_books,
            "total_users":    total_users,
            "total_emprunts": total_emprunts,
            "total_category": total_category,
        },
    )


# ── Login ──────────────────────────────────────────────────────────────────────

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)):
    user = get_optional_user(request, db)
    if user:
        return RedirectResponse("/books", status_code=302)
    return templates.TemplateResponse(
        "auth/login.html", {"request": request, "error": None}
    )


@router.post("/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, username, password)

    if not user:
        # ── Audit: failed login ────────────────────────────────────────────────
        create_audit_log(
            db,
            action="LOGIN_FAILED",
            user_id=None,
            details=f"Tentative échouée pour '{username}' depuis {request.client.host}",
        )
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Nom d'utilisateur ou mot de passe incorrect"},
            status_code=401,
        )

    request.session["user_id"] = user.id

    # ── Audit: successful login ────────────────────────────────────────────────
    create_audit_log(
        db,
        action="LOGIN",
        user_id=user.id,
        details=f"Connexion réussie depuis {request.client.host}",
    )

    return RedirectResponse("/books", status_code=302)


# ── Register ───────────────────────────────────────────────────────────────────

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request, db: Session = Depends(get_db)):
    user = get_optional_user(request, db)
    if user:
        return RedirectResponse("/books", status_code=302)
    return templates.TemplateResponse(
        "auth/register.html", {"request": request, "error": None}
    )


@router.post("/register", response_class=HTMLResponse)
def register_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    if len(username) < 3:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": "Nom d'utilisateur trop court (min 3 caractères)"},
        )
    if len(password) < 6:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": "Mot de passe trop court (min 6 caractères)"},
        )
    if get_user_by_username(db, username):
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": "Ce nom d'utilisateur est déjà pris"},
        )

    new_user = create_user(db, username=username, email=email, password=password)

    # ── Audit: new registration ────────────────────────────────────────────────
    create_audit_log(
        db,
        action="REGISTER",
        user_id=new_user.id,
        details=f"Nouveau compte créé : {username}",
    )

    return RedirectResponse("/login?registered=1", status_code=302)


# ── Logout ─────────────────────────────────────────────────────────────────────

@router.get("/logout")
def logout(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")

    if user_id:
        # ── Audit: logout ──────────────────────────────────────────────────────
        create_audit_log(
            db,
            action="LOGOUT",
            user_id=user_id,
            details="Déconnexion",
        )

    request.session.clear()
    return RedirectResponse("/login", status_code=302)