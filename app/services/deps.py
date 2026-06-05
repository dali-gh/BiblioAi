from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.models import User
from app.services.auth_service import get_user_by_id


class _LoginRedirect(Exception):
    def __init__(self):
        self.response = RedirectResponse("/login", status_code=302)


def get_current_user(request: Request, db: Session) -> User:
    user_id = request.session.get("user_id")
    if not user_id:
        raise _LoginRedirect()
    user = get_user_by_id(db, user_id)
    if not user:
        request.session.clear()
        raise _LoginRedirect()
    return user


def get_current_admin(request: Request, db: Session) -> User:
    user = get_current_user(request, db)
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")
    return user


def get_optional_user(request: Request, db: Session) -> User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return get_user_by_id(db, user_id)