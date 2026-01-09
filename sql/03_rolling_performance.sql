-- Rolling 30-day forecast accuracy
SELECT 
    date,
    garch_forecast,
    realised_volatility,
    abs_error,
    AVG(abs_error) OVER (
        ORDER BY date 
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) as rolling_30d_mae,
    AVG(forecast_error) OVER (
        ORDER BY date 
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) as rolling_30d_bias
FROM volatility_forecasts
WHERE date >= '2022-01-01'
ORDER BY date DESC;