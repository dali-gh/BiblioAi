from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import Book, BookStatus
from app.schemas import BookCreate, BookUpdate


def get_all_books(db: Session, search: str = "") -> list[Book]:
    query = db.query(Book)
    if search:
        query = query.filter(
            or_(
                Book.titre.ilike(f"%{search}%"),
                Book.auteur.ilike(f"%{search}%"),
                Book.categorie.ilike(f"%{search}%"),
            )
        )
    return query.order_by(Book.titre).all()


def get_book_by_id(db: Session, book_id: int) -> Book | None:
    return db.query(Book).filter(Book.id == book_id).first()


def create_book(db: Session, data: BookCreate) -> Book:
    book = Book(
        titre=data.titre,
        auteur=data.auteur,
        categorie=data.categorie,
        annee_publication=data.annee_publication,
        quantite_totale=data.quantite_totale,
        quantite_disponible=data.quantite_totale,
        description=data.description,
        statut=BookStatus.DISPONIBLE,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def update_book(db: Session, book_id: int, data: BookUpdate) -> Book | None:
    book = get_book_by_id(db, book_id)
    if not book:
        return None
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(book, field, value)
    if data.quantite_totale is not None:
        borrowed = book.quantite_totale - book.quantite_disponible
        book.quantite_disponible = max(0, data.quantite_totale - borrowed)
        book.update_status()
    db.commit()
    db.refresh(book)
    return book


def delete_book(db: Session, book_id: int) -> bool:
    book = get_book_by_id(db, book_id)
    if not book:
        return False
    db.delete(book)
    db.commit()
    return True


def get_books_context_for_chat(db: Session) -> str:
    """Build a text summary of the library for the AI chatbot context."""
    books = db.query(Book).all()
    if not books:
        return "La bibliothèque est vide pour le moment."

    lines = ["=== Catalogue de la bibliothèque ===\n"]
    for b in books:
        lines.append(
            f"ID: {b.id} | Titre: {b.titre} | Auteur: {b.auteur} | "
            f"Catégorie: {b.categorie} | Année: {b.annee_publication} | "
            f"Statut: {b.statut.value} | Disponible: {b.quantite_disponible}/{b.quantite_totale}"
        )
    return "\n".join(lines)
