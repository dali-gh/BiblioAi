from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.audit_service import get_all_logs, get_logs_by_user
from app.services.deps import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/admin/logs", response_class=HTMLResponse)
def audit_logs_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user.is_admin:
        return RedirectResponse("/books", status_code=302)
    logs = get_all_logs(db)
    return templates.TemplateResponse(
        "admin/auditlogs.html",
        {"request": request, "user": user, "logs": logs},
    )