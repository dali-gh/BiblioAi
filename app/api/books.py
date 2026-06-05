from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.book_service import (
    get_all_books, get_book_by_id, create_book, update_book, delete_book,
)
from app.services.deps import get_current_user, get_current_admin
from app.schemas import BookCreate, BookUpdate

router = APIRouter(prefix="/books")
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
def list_books(
    request: Request,
    search: str = "",
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    books = get_all_books(db, search=search)
    return templates.TemplateResponse(
        "books/list.html",
        {"request": request, "books": books, "search": search, "user": user},
    )


@router.get("/add", response_class=HTMLResponse)
def add_book_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_admin(request, db)
    return templates.TemplateResponse(
        "books/form.html",
        {"request": request, "user": user, "book": None, "error": None},
    )


@router.post("/add", response_class=HTMLResponse)
def add_book_submit(
    request: Request,
    titre: str = Form(...),
    auteur: str = Form(...),
    categorie: str = Form(...),
    annee_publication: int = Form(...),
    quantite_totale: int = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
):
    user = get_current_admin(request, db)
    data = BookCreate(
        titre=titre,
        auteur=auteur,
        categorie=categorie,
        annee_publication=annee_publication,
        quantite_totale=quantite_totale,
        description=description or None,
    )
    create_book(db, data)
    return RedirectResponse("/books", status_code=302)


@router.get("/{book_id}/edit", response_class=HTMLResponse)
def edit_book_page(book_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_admin(request, db)
    book = get_book_by_id(db, book_id)
    if not book:
        return RedirectResponse("/books", status_code=302)
    return templates.TemplateResponse(
        "books/form.html",
        {"request": request, "user": user, "book": book, "error": None},
    )


@router.post("/{book_id}/edit", response_class=HTMLResponse)
def edit_book_submit(
    book_id: int,
    request: Request,
    titre: str = Form(...),
    auteur: str = Form(...),
    categorie: str = Form(...),
    annee_publication: int = Form(...),
    quantite_totale: int = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
):
    user = get_current_admin(request, db)
    data = BookUpdate(
        titre=titre,
        auteur=auteur,
        categorie=categorie,
        annee_publication=annee_publication,
        quantite_totale=quantite_totale,
        description=description or None,
    )
    update_book(db, book_id, data)
    return RedirectResponse("/books", status_code=302)


@router.post("/{book_id}/delete")
def delete_book_route(book_id: int, request: Request, db: Session = Depends(get_db)):
    get_current_admin(request, db)
    delete_book(db, book_id)
    return RedirectResponse("/books", status_code=302)


@router.get("/{book_id}", response_class=HTMLResponse)
def book_detail(book_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    book = get_book_by_id(db, book_id)
    if not book:
        return RedirectResponse("/books", status_code=302)
    return templates.TemplateResponse(
        "books/detail.html",
        {"request": request, "book": book, "user": user},
    )
