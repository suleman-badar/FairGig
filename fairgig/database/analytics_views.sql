-- Privacy-safe analytics views
CREATE OR REPLACE VIEW analytics.commission_trends AS
SELECT
    platform,
    DATE_TRUNC('week', shift_date) AS week_start,
    COUNT(DISTINCT worker_id) AS worker_count,
    ROUND(AVG(
        CASE WHEN gross_earned > 0
        THEN (platform_deductions / gross_earned) * 100
        ELSE NULL END
    )::numeric, 2) AS avg_commission_pct,
    ROUND(MIN(
        CASE WHEN gross_earned > 0
        THEN (platform_deductions / gross_earned) * 100
        ELSE NULL END
    )::numeric, 2) AS min_commission_pct,
    ROUND(MAX(
        CASE WHEN gross_earned > 0
        THEN (platform_deductions / gross_earned) * 100
        ELSE NULL END
    )::numeric, 2) AS max_commission_pct
FROM earnings.shifts
WHERE verification_status = 'verified'
GROUP BY platform, DATE_TRUNC('week', shift_date)
HAVING COUNT(DISTINCT worker_id) >= 5
ORDER BY week_start DESC;

CREATE OR REPLACE VIEW analytics.city_medians AS
SELECT
    u.city_zone,
    u.worker_category,
    s.platform,
    COUNT(DISTINCT s.worker_id) AS worker_count,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (
        ORDER BY CASE WHEN s.hours_worked > 0
                 THEN s.net_received / s.hours_worked
                 ELSE NULL END
    )::numeric, 2) AS median_hourly_rate,
    ROUND(AVG(s.net_received)::numeric, 2) AS avg_daily_net
FROM earnings.shifts s
JOIN auth.users u ON s.worker_id = u.id
WHERE s.verification_status = 'verified'
  AND s.hours_worked > 0
GROUP BY u.city_zone, u.worker_category, s.platform
HAVING COUNT(DISTINCT s.worker_id) >= 5;

CREATE OR REPLACE VIEW analytics.vulnerability_flags AS
WITH monthly AS (
    SELECT
        worker_id,
        DATE_TRUNC('month', shift_date) AS month,
        u.city_zone,
        u.worker_category,
        SUM(net_received) AS monthly_net
    FROM earnings.shifts s
    JOIN auth.users u ON s.worker_id = u.id
    GROUP BY worker_id, DATE_TRUNC('month', shift_date), u.city_zone, u.worker_category
),
drops AS (
    SELECT
        m1.worker_id,
        m1.city_zone,
        m1.worker_category,
        m1.month AS current_month,
        m1.monthly_net AS current_net,
        m2.monthly_net AS prev_net,
        ROUND(((m1.monthly_net - m2.monthly_net) / NULLIF(m2.monthly_net, 0) * 100)::numeric, 1)
            AS pct_change
    FROM monthly m1
    JOIN monthly m2
        ON m1.worker_id = m2.worker_id
        AND m1.month = m2.month + INTERVAL '1 month'
    WHERE m2.monthly_net > 0
      AND m1.monthly_net < m2.monthly_net * 0.80
)
SELECT
    city_zone,
    worker_category,
    current_month,
    COUNT(*) AS flagged_worker_count,
    ROUND(AVG(pct_change)::numeric, 1) AS avg_pct_drop
FROM drops
GROUP BY city_zone, worker_category, current_month
HAVING COUNT(*) >= 3;
