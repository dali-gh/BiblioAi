"""
Run this script to populate the database with sample books.
Usage: python seed.py
"""
from app.database import SessionLocal, engine, Base
from app.models import Book, BookStatus
from app.services.auth_service import create_user, get_user_by_username

Base.metadata.create_all(bind=engine)

SAMPLE_BOOKS = [
    {
        "titre": "Le Petit Prince",
        "auteur": "Antoine de Saint-Exupéry",
        "categorie": "Roman",
        "annee_publication": 1943,
        "quantite_totale": 3,
        "description": "Un conte philosophique et poétique sur l'amitié et la vie.",
    },
    {
        "titre": "Les Misérables",
        "auteur": "Victor Hugo",
        "categorie": "Roman",
        "annee_publication": 1862,
        "quantite_totale": 2,
        "description": "L'épopée de Jean Valjean dans la France du XIXe siècle.",
    },
    {
        "titre": "Notre-Dame de Paris",
        "auteur": "Victor Hugo",
        "categorie": "Roman",
        "annee_publication": 1831,
        "quantite_totale": 2,
        "description": "L'histoire tragique de Quasimodo et d'Esmeralda.",
    },
    {
        "titre": "Orgueil et Préjugés",
        "auteur": "Jane Austen",
        "categorie": "Roman",
        "annee_publication": 1813,
        "quantite_totale": 2,
        "description": "Une satire sociale de la société anglaise du XIXe siècle.",
    },
    {
        "titre": "Python pour les nuls",
        "auteur": "John Paul Mueller",
        "categorie": "Informatique",
        "annee_publication": 2020,
        "quantite_totale": 4,
        "description": "Guide complet pour apprendre Python de zéro.",
    },
    {
        "titre": "Clean Code",
        "auteur": "Robert C. Martin",
        "categorie": "Informatique",
        "annee_publication": 2008,
        "quantite_totale": 3,
        "description": "Les principes du code propre et maintenable.",
    },
    {
        "titre": "Sapiens",
        "auteur": "Yuval Noah Harari",
        "categorie": "Histoire",
        "annee_publication": 2011,
        "quantite_totale": 3,
        "description": "Une brève histoire de l'humanité.",
    },
    {
        "titre": "L'Étranger",
        "auteur": "Albert Camus",
        "categorie": "Roman",
        "annee_publication": 1942,
        "quantite_totale": 2,
        "description": "Le roman existentialiste de Camus sur Meursault.",
    },
    {
        "titre": "Le Comte de Monte-Cristo",
        "auteur": "Alexandre Dumas",
        "categorie": "Roman",
        "annee_publication": 1844,
        "quantite_totale": 2,
        "description": "Le chef-d'œuvre de vengeance et de justice d'Edmond Dantès.",
    },
    {
        "titre": "Introduction à l'Intelligence Artificielle",
        "auteur": "Stuart Russell",
        "categorie": "Informatique",
        "annee_publication": 2020,
        "quantite_totale": 2,
        "description": "Les fondements de l'IA moderne.",
    },
]


def seed():
    db = SessionLocal()
    try:
        # Admin user
        if not get_user_by_username(db, "admin"):
            create_user(db, "admin", "admin@bibliotheque.com", "admin123", is_admin=True)
            print("✅ Admin créé : admin / admin123")

        # Regular user
        if not get_user_by_username(db, "lecteur"):
            create_user(db, "lecteur", "lecteur@bibliotheque.com", "lecteur123")
            print("✅ Lecteur créé : lecteur / lecteur123")

        # Books
        existing = db.query(Book).count()
        if existing == 0:
            for data in SAMPLE_BOOKS:
                book = Book(
                    **data,
                    quantite_disponible=data["quantite_totale"],
                    statut=BookStatus.DISPONIBLE,
                )
                db.add(book)
            db.commit()
            print(f"✅ {len(SAMPLE_BOOKS)} livres ajoutés")
        else:
            print(f"ℹ️  {existing} livre(s) déjà dans la base")

        print("\n🚀 Base de données prête !")
        print("   Lancez : uvicorn app.main:app --reload")
        print("   Accès  : http://localhost:8000")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
