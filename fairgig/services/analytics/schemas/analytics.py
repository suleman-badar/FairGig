from pydantic import BaseModel


class CommissionTrend(BaseModel):
    week_start: str
    platform: str
    avg_commission_pct: float
    worker_count: int


class WorkerMedian(BaseModel):
    city_zone: str
    worker_category: str
    platform: str
    worker_count: int
    median_hourly_rate: float
    avg_daily_net: float
