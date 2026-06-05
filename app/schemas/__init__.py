from datetime import date, datetime
from pydantic import BaseModel, EmailStr, field_validator
from app.models import BookStatus, BorrowStatus


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def username_min_length(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError("Le nom d'utilisateur doit avoir au moins 3 caractères")
        return v

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Le mot de passe doit avoir au moins 6 caractères")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Books ─────────────────────────────────────────────────────────────────────

class BookCreate(BaseModel):
    titre: str
    auteur: str
    categorie: str
    annee_publication: int
    quantite_totale: int = 1
    description: str | None = None

    @field_validator("annee_publication")
    @classmethod
    def valid_year(cls, v: int) -> int:
        if v < 1000 or v > 2100:
            raise ValueError("Année invalide")
        return v

    @field_validator("quantite_totale")
    @classmethod
    def positive_qty(cls, v: int) -> int:
        if v < 1:
            raise ValueError("La quantité doit être au moins 1")
        return v


class BookUpdate(BaseModel):
    titre: str | None = None
    auteur: str | None = None
    categorie: str | None = None
    annee_publication: int | None = None
    quantite_totale: int | None = None
    description: str | None = None


class BookOut(BaseModel):
    id: int
    titre: str
    auteur: str
    categorie: str
    annee_publication: int
    quantite_disponible: int
    quantite_totale: int
    statut: BookStatus
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Borrow ────────────────────────────────────────────────────────────────────

class BorrowCreate(BaseModel):
    book_id: int
    date_retour_prevue: date


class BorrowOut(BaseModel):
    id: int
    user_id: int
    book_id: int
    date_emprunt: date
    date_retour_prevue: date
    date_retour_effective: date | None
    statut: BorrowStatus

    model_config = {"from_attributes": True}


# ── Chat ──────────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


# ── Audit logs ──────────────────────────────────────────────────────────────────────

class AuditLogCreate(BaseModel):
    user_id: int | None = None
    action: str
    details: str | None = None


class AuditLogOut(BaseModel):
    id: int
    user_id: int | None
    action: str
    details: str | None
    timestamp: datetime

    model_config = {"from_attributes": True}

class AuditLogFilter(BaseModel):
    user_id: int | None = None
    action: str | None = None
    date_from: date | None = None
    date_to: date | None = None