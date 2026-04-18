from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db

router = APIRouter(prefix='/analytics', tags=['analytics'])


@router.get('/worker-median')
def worker_median(
    city_zone: str = Query(...),
    worker_category: str = Query(...),
    platform: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    sql = """
        SELECT city_zone, worker_category, platform, worker_count, median_hourly_rate, avg_daily_net
        FROM analytics.city_medians
        WHERE city_zone = :city_zone
          AND worker_category = :worker_category
          AND (:platform IS NULL OR platform = :platform)
        ORDER BY worker_count DESC
        LIMIT 1
    """
    row = db.execute(
        text(sql),
        {'city_zone': city_zone, 'worker_category': worker_category, 'platform': platform},
    ).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail='No aggregate data found')

    return dict(row)


@router.get('/income-distribution')
def income_distribution(db: Session = Depends(get_db)):
    sql = """
        SELECT
            city_zone,
            CASE
                WHEN avg_daily_net < 1000 THEN 'under_1000'
                WHEN avg_daily_net < 2000 THEN '1000_to_1999'
                WHEN avg_daily_net < 4000 THEN '2000_to_3999'
                ELSE '4000_plus'
            END AS bracket,
            COUNT(*) AS count
        FROM analytics.city_medians
        GROUP BY city_zone, bracket
        ORDER BY city_zone, bracket
    """
    rows = db.execute(text(sql)).mappings().all()
    return {'items': [dict(r) for r in rows]}
