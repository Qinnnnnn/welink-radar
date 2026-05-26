"""Recover route — create SQLite backup via VACUUM INTO."""

from fastapi import APIRouter
from core.config import DATA_DIR
from core.database import DB_PATH, get_db

router = APIRouter(prefix="/api/recover", tags=["recover"])


@router.post("")
async def recover():
    """Create a recovered SQLite copy."""
    import os
    dest = DATA_DIR / "radar_recovered.db"
    db = get_db()
    try:
        db.execute(f"VACUUM INTO '{dest}'")
        size = os.path.getsize(str(dest)) if dest.exists() else 0
        return {"ok": True, "dest": str(dest), "size": size}
    except Exception as e:
        return {"ok": False, "error": str(e)}
