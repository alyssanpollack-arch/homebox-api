from fastapi import Depends, Request
from sqlalchemy.orm import Session

from database import get_db
from models import Member


def get_current_member(request: Request, db: Session = Depends(get_db)) -> Member | None:
    """Extract Bearer token from Authorization header and look up the member.
    Returns None if invalid — callers return a 200 error response for Siri compatibility."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.removeprefix("Bearer ").strip()
    if not token:
        return None
    return db.query(Member).filter(Member.token == token).first()
