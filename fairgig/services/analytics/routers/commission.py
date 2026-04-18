from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db

router = APIRouter(prefix='/analytics', tags=['analytics'])


@router.get('/commission-trends')
def commission_trends(
    platform: str | None = Query(default=None),
    weeks: int = Query(default=12, ge=1, le=104),
    db: Session = Depends(get_db),
):
    sql = """
        SELECT week_start, platform, avg_commission_pct, worker_count
        FROM analytics.commission_trends
        WHERE (:platform IS NULL OR platform = :platform)
        ORDER BY week_start DESC
        LIMIT :weeks
    """
    rows = db.execute(text(sql), {'platform': platform, 'weeks': weeks}).mappings().all()
    return {'items': [dict(r) for r in rows]}
