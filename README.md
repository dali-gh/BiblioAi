# Bibliothèque Intelligente — FastAPI + Bootstrap + SQLite + Gemini AI

Projet semestriel Python — AU 2025-2026  
**Stack** : FastAPI · Bootstrap 5 · Jinja2 · SQLite · SQLAlchemy · Google Gemini AI  
**Auth** : Sessions (cookies) 
**version**: 1.0.0

---

## Structure du projet

```
bibliotheque/
├── app/
│   ├── main.py              # Point d'entrée FastAPI
│   ├── config.py            # Configuration & variables d'environnement
│   ├── database.py          # SQLAlchemy engine & session
│   ├── models/
│   │   └── __init__.py      # Modèles SQLAlchemy (User, Book, Borrow, Chathistory, audit_logs)
│   ├── schemas/
│   │   └── __init__.py      # Schémas Pydantic (validation)
│   ├── services/
│   │   ├── auth_service.py  # Hashage mot de passe, authentification
│   │   ├── book_service.py  # CRUD des livres
│   │   ├── borrow_service.py# Logique d'emprunt / retour
|   |   |── audit_service    # Audit logs
│   │   ├── ai_service.py    # Chatbot Gemini AI
│   │   └── deps.py          # Dépendances (get_current_user…)
│   ├── api/
│   │   ├── auth.py          # Routes /login, /register, /logout
│   │   ├── books.py         # Routes /books (CRUD)
|   |   ├── audit.py         # Routes /audit_logs 
│   │   ├── borrow.py        # Routes /borrows
│   │   └── chat.py          # Routes /chat
│   ├── templates/           # Templates Jinja2 (Ninja2)
│   │   ├── base.html
│   │   ├── auth/
|   |   |── admin/
│   │   ├── books/
│   │   ├── borrow/
│   │   └── chat/
│   └── static/              # CSS / JS statiques (optionnel)
├── seed.py                  # Peuplement de la base avec des données exemples
├── core/
    |── security.py          # requirement of admin_role
├── requirements.txt
└── .env
```



## Authentification

L'authentification est basée sur les **sessions cookie** (ItsDangerous / Starlette SessionMiddleware).  
Pas de JWT, pas de token complexe — simple et efficace pour une application web.

| Rôle    | Accès                                                     |
|---------|-----------------------------------------------------------|
| Lecteur | Voir les livres, emprunter, voir ses propres emprunts     |
| Admin   | Tout + ajouter/modifier/supprimer des livres, voir tous les emprunts |

---

## Chatbot IA 

Le chatbot utilise **Google Gemini 1.5 Flash** (gratuit).  
À chaque question, il reçoit en contexte le catalogue complet de la bibliothèque et répond en français avec des données réelles.

Exemples de questions supportées :
- "Est-ce que le livre avec l'ID 3 est disponible ?"
- "Quels livres de Victor Hugo avez-vous ?"
- "Recommande-moi un roman romantique facile à lire"
- "Combien d'exemplaires de Clean Code restent-ils ?"

---

## Technologies utilisées

| Composant      | Technologie            |
|----------------|------------------------|
| Backend        | FastAPI                |
| Templates      | Jinja2 (Ninja2)        |
| Base de données| SQLite + SQLAlchemy 2  |
| Frontend       | Bootstrap 5            |
| Auth           | Sessions cookie        |
| IA Chatbot     | Google Gemini 1.5 Flash|
| Validation     | Pydantic v2            |
| Sécurité mdp   | bcrypt (passlib)       |
