-- Main dataset for Power BI dashboard
WITH latest_regime AS (
    SELECT regime, date
    FROM volatility_regimes
    ORDER BY date DESC
    LIMIT 1
)
SELECT 
    vf.date,
    vf.garch_forecast,
    vf.realised_volatility,
    vf.forecast_error,
    vf.abs_error,
    vr.regime,
    vr.percentile_rank,
    CASE 
        WHEN vf.garch_forecast > 0.015 THEN 'High Risk'
        WHEN vf.garch_forecast > 0.010 THEN 'Medium Risk'
        ELSE 'Low Risk'
    END as risk_level,
    AVG(vf.abs_error) OVER (
        ORDER BY vf.date 
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) as rolling_30d_mae,
    CASE 
        WHEN vr.regime = lr.regime THEN true 
        ELSE false 
    END as is_current_regime
FROM volatility_forecasts vf
LEFT JOIN volatility_regimes vr ON vf.date = vr.date
CROSS JOIN latest_regime lr
WHERE vf.date >= '2022-01-01'
ORDER BY vf.date DESC;