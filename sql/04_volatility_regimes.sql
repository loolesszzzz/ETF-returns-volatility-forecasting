-- Current regime and regime statistics
WITH regime_stats AS (
    SELECT 
        regime,
        COUNT(*) as days_in_regime,
        AVG(realised_volatility) as avg_volatility,
        MIN(realised_volatility) as min_volatility,
        MAX(realised_volatility) as max_volatility
    FROM volatility_regimes
    GROUP BY regime
),
current_regime AS (
    SELECT 
        regime,
        date,
        realised_volatility
    FROM volatility_regimes
    ORDER BY date DESC
    LIMIT 1
)
SELECT 
    rs.regime,
    rs.days_in_regime,
    ROUND(rs.avg_volatility::numeric, 6) as avg_volatility,
    ROUND(rs.min_volatility::numeric, 6) as min_volatility,
    ROUND(rs.max_volatility::numeric, 6) as max_volatility,
    CASE 
        WHEN cr.regime = rs.regime THEN 'CURRENT'
        ELSE ''
    END as status
FROM regime_stats rs
CROSS JOIN current_regime cr
ORDER BY rs.avg_volatility DESC;