from datetime import date
from sqlalchemy.orm import Session, joinedload
from app.models import Borrow, Book, BorrowStatus
from app.schemas import BorrowCreate


def get_user_borrows(db: Session, user_id: int) -> list[Borrow]:
    return (
        db.query(Borrow)
        .options(joinedload(Borrow.book))
        .filter(Borrow.user_id == user_id)
        .order_by(Borrow.date_emprunt.desc())
        .all()
    )


def get_all_borrows(db: Session) -> list[Borrow]:
    return (
        db.query(Borrow)
        .options(joinedload(Borrow.book), joinedload(Borrow.user))
        .order_by(Borrow.date_emprunt.desc())
        .all()
    )


def borrow_book(db: Session, user_id: int, data: BorrowCreate) -> tuple[Borrow | None, str]:
    book = db.query(Book).filter(Book.id == data.book_id).first()
    if not book:
        return None, "Livre introuvable."
    if book.quantite_disponible <= 0:
        return None, "Ce livre n'est plus disponible."
    if data.date_retour_prevue <= date.today():
        return None, "La date de retour doit être dans le futur."

    # Check if user already has this book
    existing = (
        db.query(Borrow)
        .filter(
            Borrow.user_id == user_id,
            Borrow.book_id == data.book_id,
            Borrow.statut == BorrowStatus.EN_COURS,
        )
        .first()
    )
    if existing:
        return None, "Vous avez déjà emprunté ce livre."

    borrow = Borrow(
        user_id=user_id,
        book_id=data.book_id,
        date_retour_prevue=data.date_retour_prevue,
        statut=BorrowStatus.EN_COURS,
    )
    book.quantite_disponible -= 1
    book.update_status()

    db.add(borrow)
    db.commit()
    db.refresh(borrow)
    return borrow, "Emprunt enregistré avec succès."


def return_book(db: Session, borrow_id: int, user_id: int) -> tuple[bool, str]:
    borrow = (
        db.query(Borrow)
        .filter(Borrow.id == borrow_id, Borrow.user_id == user_id)
        .first()
    )
    if not borrow:
        return False, "Emprunt introuvable."
    if borrow.statut == BorrowStatus.RETOURNE:
        return False, "Ce livre a déjà été retourné."

    borrow.statut = BorrowStatus.RETOURNE
    borrow.date_retour_effective = date.today()

    book = db.query(Book).filter(Book.id == borrow.book_id).first()
    if book:
        book.quantite_disponible += 1
        book.update_status()

    db.commit()
    return True, "Retour enregistré avec succès."
