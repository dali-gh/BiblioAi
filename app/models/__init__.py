from datetime import datetime, date
from enum import Enum as PyEnum

from sqlalchemy import (
    Integer, String, Text, Date, DateTime,
    ForeignKey, Boolean, func, Enum as SAEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# =========================
# ENUMS
# =========================

class BookStatus(str, PyEnum):
    DISPONIBLE = "disponible"
    EMPRUNTE = "emprunté"
    RESERVE = "réservé"


class BorrowStatus(str, PyEnum):
    EN_COURS = "en_cours"
    RETOURNE = "retourné"
    EN_RETARD = "en_retard"


# =========================
# USER MODEL
# =========================

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    borrows: Mapped[list["Borrow"]] = relationship("Borrow", back_populates="user")
    chat_messages: Mapped[list["ChatHistory"]] = relationship("ChatHistory", back_populates="user")
    audit_logs: Mapped[list["AuditLog"]] = relationship("AuditLog", back_populates="user")


# =========================
# BOOK MODEL
# =========================

class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    titre: Mapped[str] = mapped_column(String(200), nullable=False)
    auteur: Mapped[str] = mapped_column(String(100), nullable=False)
    categorie: Mapped[str] = mapped_column(String(50), nullable=False)
    annee_publication: Mapped[int] = mapped_column(Integer, nullable=False)

    quantite_disponible: Mapped[int] = mapped_column(Integer, default=1)
    quantite_totale: Mapped[int] = mapped_column(Integer, default=1)

    statut: Mapped[BookStatus] = mapped_column(
        SAEnum(BookStatus, native_enum=False),
        default=BookStatus.DISPONIBLE
    )

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    borrows: Mapped[list["Borrow"]] = relationship("Borrow", back_populates="book")

    def update_status(self):
        if self.quantite_disponible <= 0:
            self.statut = BookStatus.EMPRUNTE
        else:
            self.statut = BookStatus.DISPONIBLE


# =========================
# BORROW MODEL
# =========================

class Borrow(Base):
    __tablename__ = "borrows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)

    date_emprunt: Mapped[date] = mapped_column(Date, default=date.today)
    date_retour_prevue: Mapped[date] = mapped_column(Date, nullable=False)
    date_retour_effective: Mapped[date | None] = mapped_column(Date, nullable=True)

    statut: Mapped[BorrowStatus] = mapped_column(
        SAEnum(BorrowStatus, native_enum=False),
        default=BorrowStatus.EN_COURS
    )

    user: Mapped["User"] = relationship("User", back_populates="borrows")
    book: Mapped["Book"] = relationship("Book", back_populates="borrows")


# =========================
# CHAT HISTORY
# =========================

class ChatHistory(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    message: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="chat_messages")


# =========================
# AUDIT LOG
# =========================

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    action: Mapped[str] = mapped_column(String(100), nullable=False)
    details: Mapped[str | None] = mapped_column(String(255), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="audit_logs")