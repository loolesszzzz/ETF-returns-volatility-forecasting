-- Latest 30 days of forecasts with risk classification
SELECT 
    date,
    garch_forecast,
    realised_volatility,
    abs_error,
    CASE 
        WHEN garch_forecast > 0.015 THEN 'High Risk'
        WHEN garch_forecast > 0.010 THEN 'Medium Risk'
        ELSE 'Low Risk'
    END as risk_level
FROM volatility_forecasts
WHERE date >= DATE '2024-12-31' - INTERVAL '30 days'
ORDER BY date DESC;