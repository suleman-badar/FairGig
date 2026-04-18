-- ============================================================
-- FairGig Database Initialisation
-- ============================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create schemas for logical separation
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS earnings;
CREATE SCHEMA IF NOT EXISTS grievance;
CREATE SCHEMA IF NOT EXISTS analytics;

-- ============================================================
-- SCHEMA: auth
-- ============================================================

CREATE TABLE IF NOT EXISTS auth.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone VARCHAR(15) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash TEXT NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) NOT NULL
        CHECK (role IN ('worker', 'verifier', 'advocate', 'admin')),
    city_zone VARCHAR(50),
    worker_category VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS auth.refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- SCHEMA: earnings
-- ============================================================

CREATE TABLE IF NOT EXISTS earnings.shifts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    worker_id UUID NOT NULL,
    platform VARCHAR(50) NOT NULL
        CHECK (platform IN (
            'Careem', 'Bykea', 'inDrive',
            'Foodpanda', 'Cheetay',
            'Daraz', 'Rozee',
            'Freelance_Upwork', 'Freelance_Fiverr', 'Freelance_Other',
            'Domestic', 'Other'
        )),
    shift_date DATE NOT NULL,
    hours_worked NUMERIC(4,2) NOT NULL CHECK (hours_worked >= 0),
    gross_earned NUMERIC(10,2) NOT NULL CHECK (gross_earned >= 0),
    platform_deductions NUMERIC(10,2) NOT NULL DEFAULT 0
        CHECK (platform_deductions >= 0),
    net_received NUMERIC(10,2) NOT NULL
        CHECK (net_received >= 0),
    notes TEXT,

    screenshot_filename TEXT,
    screenshot_uploaded_at TIMESTAMPTZ,
    verification_status VARCHAR(20) NOT NULL DEFAULT 'unsubmitted'
        CHECK (verification_status IN (
            'unsubmitted',
            'pending',
            'verified',
            'discrepancy',
            'unverifiable'
        )),
    verifier_id UUID,
    verifier_note TEXT,
    verified_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT positive_net CHECK (net_received <= gross_earned)
);

CREATE INDEX IF NOT EXISTS idx_shifts_worker_id ON earnings.shifts(worker_id);
CREATE INDEX IF NOT EXISTS idx_shifts_date ON earnings.shifts(shift_date);
CREATE INDEX IF NOT EXISTS idx_shifts_platform ON earnings.shifts(platform);
CREATE INDEX IF NOT EXISTS idx_shifts_verification ON earnings.shifts(verification_status);

-- ============================================================
-- SCHEMA: grievance
-- ============================================================

CREATE TABLE IF NOT EXISTS grievance.complaints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    worker_id UUID NOT NULL,
    platform VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL
        CHECK (category IN (
            'commission_rate_change',
            'account_deactivation',
            'payment_delay',
            'incorrect_calculation',
            'unsafe_working_condition',
            'no_transparency',
            'other'
        )),
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,

    status VARCHAR(20) NOT NULL DEFAULT 'open'
        CHECK (status IN ('open', 'under_review', 'escalated', 'resolved', 'rejected')),
    tags TEXT[] DEFAULT '{}',
    cluster_id UUID,
    advocate_note TEXT,
    escalated_by UUID,
    escalated_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,

    is_public BOOLEAN DEFAULT TRUE,
    anonymous_display_id VARCHAR(10),

    upvotes INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS grievance.clusters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    label VARCHAR(200) NOT NULL,
    description TEXT,
    platform VARCHAR(50),
    created_by UUID NOT NULL,
    complaint_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active'
        CHECK (status IN ('active', 'escalated', 'resolved')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'fk_cluster'
    ) THEN
        ALTER TABLE grievance.complaints
            ADD CONSTRAINT fk_cluster FOREIGN KEY (cluster_id)
            REFERENCES grievance.clusters(id) ON DELETE SET NULL;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_complaints_worker ON grievance.complaints(worker_id);
CREATE INDEX IF NOT EXISTS idx_complaints_platform ON grievance.complaints(platform);
CREATE INDEX IF NOT EXISTS idx_complaints_status ON grievance.complaints(status);
CREATE INDEX IF NOT EXISTS idx_complaints_cluster ON grievance.complaints(cluster_id);

-- ============================================================
-- PRIVACY-SAFE ANALYTICS VIEWS
-- ============================================================

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

-- ============================================================
-- DATABASE-LEVEL ROLE FOR ANALYTICS SERVICE
-- ============================================================
-- CREATE ROLE analytics_reader WITH LOGIN PASSWORD 'change_in_production';
-- GRANT USAGE ON SCHEMA analytics TO analytics_reader;
-- GRANT SELECT ON analytics.commission_trends TO analytics_reader;
-- GRANT SELECT ON analytics.city_medians TO analytics_reader;
-- GRANT SELECT ON analytics.vulnerability_flags TO analytics_reader;
-- GRANT USAGE ON SCHEMA grievance TO analytics_reader;
-- GRANT SELECT ON grievance.complaints TO analytics_reader;
-- REVOKE ALL ON earnings.shifts FROM analytics_reader;
