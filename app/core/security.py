from fastapi import Depends, HTTPException
from app.database import get_db
from app.services.deps import get_current_user
from sqlalchemy.orm import Session


def require_admin(request, db: Session = Depends(get_db)):
    """Use directly in routes as a dependency."""
    user = get_current_user(request, db)
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return user