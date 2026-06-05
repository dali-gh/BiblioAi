from sqlalchemy.orm import Session, joinedload
from app.models import AuditLog


def create_audit_log(
    db: Session,
    action: str,
    user_id: int | None = None,
    details: str | None = None,
) -> AuditLog:
    log = AuditLog(user_id=user_id, action=action, details=details)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_all_logs(db: Session) -> list[AuditLog]:
    return (
        db.query(AuditLog)
        .options(joinedload(AuditLog.user))
        .order_by(AuditLog.timestamp.desc())
        .all()
    )


def get_logs_by_user(db: Session, user_id: int) -> list[AuditLog]:
    return (
        db.query(AuditLog)
        .filter(AuditLog.user_id == user_id)
        .order_by(AuditLog.timestamp.desc())
        .all()
    )