from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db

router = APIRouter(prefix='/analytics', tags=['analytics'])


@router.get('/top-complaints')
def top_complaints(db: Session = Depends(get_db)):
    sql = """
        SELECT category, platform, COUNT(*)::int AS count
        FROM grievance.complaints
        WHERE created_at >= NOW() - INTERVAL '7 days'
        GROUP BY category, platform
        HAVING COUNT(*) >= 3
        ORDER BY count DESC
        LIMIT 20
    """
    rows = db.execute(text(sql)).mappings().all()
    return {'items': [dict(r) for r in rows]}
