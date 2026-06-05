import os
import google.generativeai as genai
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.services.book_service import get_books_context_for_chat

# 🔥 Load .env
load_dotenv()

# =========================
# 🔑 API KEY CONFIG
# =========================
API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ API Key manquante. Vérifie ton fichier .env")

genai.configure(api_key=API_KEY)

# see availavble ai models
# for m in genai.list_models():
#     print(m.name)


# =========================
# 🧠 SYSTEM PROMPT
# =========================
SYSTEM_PROMPT = """
Tu es un assistant intelligent pour la Bibliothèque Intelligente.
Tu réponds en français, de façon précise et conviviale.
Tu utilises uniquement les données réelles du catalogue fourni pour répondre.
Si une information n'est pas dans le catalogue, dis-le clairement.
Ne jamais inventer des livres ou des données.

Voici les données actuelles du catalogue :
{catalogue}
"""


# =========================
# 🤖 CHAT FUNCTION
# =========================
def get_chat_response(db: Session, user_message: str) -> str:
    try:
        # 📚 Get books context from DB
        catalogue = get_books_context_for_chat(db)

        # 🧾 Build prompt
        prompt = SYSTEM_PROMPT.format(catalogue=catalogue)

        # ⚡ Model (stable version)
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=prompt,
        )

        # 💬 Generate response
        response = model.generate_content(user_message)

        return response.text

    except Exception as e:
        # return f"❌ Erreur IA : {str(e)}"
        return f"Je suis désolé, l’assistant IA est temporairement indisponible. Voici les informations du catalogue de la bibliothèque."