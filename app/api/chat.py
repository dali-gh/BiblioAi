from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.ai_service import get_chat_response
from app.services.deps import get_current_user
from app.schemas import ChatMessage
from app.models import ChatHistory

router = APIRouter(prefix="/chat")
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
def chat_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    messages = (
        db.query(ChatHistory)
        .filter(ChatHistory.user_id == user.id)
        .order_by(ChatHistory.created_at.asc())
        .all()
    )

    return templates.TemplateResponse(
        "chat/chat.html",
        {
            "request": request,
            "user": user,
            "messages": messages,
        },
    )


@router.post("/ask", response_class=JSONResponse)
async def ask(
    request: Request,
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    body = await request.json()
    message = body.get("message", "").strip()
    if not message:
        return JSONResponse({"response": "Veuillez entrer un message."})
    response = get_chat_response(db, message)

    chat = ChatHistory(
    user_id=user.id,
    message=message,
    response=response
    )

    db.add(chat)
    db.commit()

    return JSONResponse({"response": response})
