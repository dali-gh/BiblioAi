from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.database import get_db
from app.services.borrow_service import (
    get_user_borrows, get_all_borrows, borrow_book, return_book,
)
from app.services.book_service import get_book_by_id
from app.services.deps import get_current_user, get_current_admin
from app.schemas import BorrowCreate

router = APIRouter(prefix="/borrows")
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
def my_borrows(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    borrows = get_user_borrows(db, user.id)
    today = date.today()
    return templates.TemplateResponse(
        "borrow/my_borrows.html",
        {"request": request, "user": user, "borrows": borrows, "today": today},
    )


@router.get("/all", response_class=HTMLResponse)
def all_borrows(request: Request, db: Session = Depends(get_db)):
    user = get_current_admin(request, db)
    borrows = get_all_borrows(db)
    today = date.today()
    return templates.TemplateResponse(
        "borrow/all_borrows.html",
        {"request": request, "user": user, "borrows": borrows, "today": today},
    )


@router.get("/new/{book_id}", response_class=HTMLResponse)
def borrow_form(book_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    book = get_book_by_id(db, book_id)
    if not book:
        return RedirectResponse("/books", status_code=302)
    default_return = date.today() + timedelta(days=14)
    return templates.TemplateResponse(
        "borrow/form.html",
        {
            "request": request,
            "user": user,
            "book": book,
            "default_return": default_return,
            "error": None,
        },
    )


@router.post("/new/{book_id}", response_class=HTMLResponse)
def borrow_submit(
    book_id: int,
    request: Request,
    date_retour_prevue: date = Form(...),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    book = get_book_by_id(db, book_id)
    data = BorrowCreate(book_id=book_id, date_retour_prevue=date_retour_prevue)
    borrow, message = borrow_book(db, user.id, data)
    if not borrow:
        default_return = date.today() + timedelta(days=14)
        return templates.TemplateResponse(
            "borrow/form.html",
            {
                "request": request,
                "user": user,
                "book": book,
                "default_return": default_return,
                "error": message,
            },
        )
    return RedirectResponse("/borrows?success=1", status_code=302)


@router.post("/{borrow_id}/return")
def return_borrow(borrow_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    return_book(db, borrow_id, user.id)
    return RedirectResponse("/borrows", status_code=302)
