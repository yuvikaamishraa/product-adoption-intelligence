-- Project demo schema: product_events
-- Note: data is synthetic demonstration data, one row per assigned user.

-- 1. Experiment group size and conversion rate
SELECT
    experiment_group,
    COUNT(DISTINCT user_id) AS assigned_users,
    SUM(converted) AS conversions,
    1.0 * SUM(converted) / COUNT(DISTINCT user_id) AS conversion_rate
FROM product_events
GROUP BY experiment_group;

-- 2. Feature adoption by platform
SELECT
    platform,
    experiment_group,
    COUNT(DISTINCT user_id) AS users,
    SUM(feature_used) AS feature_users,
    1.0 * SUM(feature_used) / COUNT(DISTINCT user_id) AS adoption_rate
FROM product_events
GROUP BY platform, experiment_group
ORDER BY platform, experiment_group;

-- 3. Conversion by user type
SELECT
    user_type,
    experiment_group,
    COUNT(DISTINCT user_id) AS users,
    SUM(converted) AS conversions,
    1.0 * SUM(converted) / COUNT(DISTINCT user_id) AS conversion_rate
FROM product_events
GROUP BY user_type, experiment_group
ORDER BY user_type, experiment_group;

-- 4. Weekly trend
SELECT
    assigned_at,
    experiment_group,
    COUNT(DISTINCT user_id) AS users,
    1.0 * SUM(converted) / COUNT(DISTINCT user_id) AS conversion_rate
FROM product_events
GROUP BY assigned_at, experiment_group
ORDER BY assigned_at, experiment_group;

-- 5. Investigate exposure / instrumentation gaps
SELECT
    experiment_group,
    COUNT(*) AS assigned_users,
    SUM(exposed) AS exposed_users,
    1.0 * SUM(exposed) / COUNT(*) AS exposure_rate,
    SUM(feature_used) AS feature_users
FROM product_events
GROUP BY experiment_group;
