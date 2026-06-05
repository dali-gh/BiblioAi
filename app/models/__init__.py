from datetime import datetime, date
from enum import Enum as PyEnum

from sqlalchemy import (
    Integer, String, Text, Date, DateTime,
    ForeignKey, Boolean, func, Enum as SAEnum
)
from sqlalchemy.orm import mapped_column, relationship

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

    id = mapped_column(Integer, primary_key=True, index=True)
    username = mapped_column(String(50), unique=True, nullable=False)
    email = mapped_column(String(100), unique=True, nullable=False)
    hashed_password = mapped_column(String(255), nullable=False)
    is_admin = mapped_column(Boolean, default=False)
    created_at = mapped_column(DateTime, default=func.now())

    borrows = relationship("Borrow", back_populates="user")
    chat_messages = relationship("ChatHistory", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


# =========================
# BOOK MODEL
# =========================

class Book(Base):
    __tablename__ = "books"

    id = mapped_column(Integer, primary_key=True, index=True)
    titre = mapped_column(String(200), nullable=False)
    auteur = mapped_column(String(100), nullable=False)
    categorie = mapped_column(String(50), nullable=False)
    annee_publication = mapped_column(Integer, nullable=False)

    quantite_disponible = mapped_column(Integer, default=1)
    quantite_totale = mapped_column(Integer, default=1)

    # ✅ FIXED (Render-safe)
    statut = mapped_column(
        SAEnum(BookStatus, native_enum=False),
        default=BookStatus.DISPONIBLE
    )

    description = mapped_column(Text, nullable=True)
    created_at = mapped_column(DateTime, default=func.now())

    borrows = relationship("Borrow", back_populates="book")

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

    id = mapped_column(Integer, primary_key=True, index=True)

    user_id = mapped_column(ForeignKey("users.id"), nullable=False)
    book_id = mapped_column(ForeignKey("books.id"), nullable=False)

    date_emprunt = mapped_column(Date, default=date.today)
    date_retour_prevue = mapped_column(Date, nullable=False)
    date_retour_effective = mapped_column(Date, nullable=True)

    statut = mapped_column(
        SAEnum(BorrowStatus, native_enum=False),
        default=BorrowStatus.EN_COURS
    )

    user = relationship("User", back_populates="borrows")
    book = relationship("Book", back_populates="borrows")


# =========================
# CHAT HISTORY
# =========================

class ChatHistory(Base):
    __tablename__ = "chat_messages"

    id = mapped_column(Integer, primary_key=True, index=True)
    user_id = mapped_column(ForeignKey("users.id"), nullable=False)

    message = mapped_column(Text, nullable=False)
    response = mapped_column(Text, nullable=False)

    created_at = mapped_column(DateTime, default=func.now())

    user = relationship("User", back_populates="chat_messages")


# =========================
# AUDIT LOG
# =========================

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = mapped_column(Integer, primary_key=True, index=True)

    user_id = mapped_column(ForeignKey("users.id"), nullable=True)

    action = mapped_column(String(100), nullable=False)
    details = mapped_column(String(255), nullable=True)
    timestamp = mapped_column(DateTime, default=func.now())

    user = relationship("User", back_populates="audit_logs")