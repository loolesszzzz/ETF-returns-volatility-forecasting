-- Model performance comparison with ranking
SELECT 
    model_name,
    mae,
    rmse,
    observation_count,
    RANK() OVER (ORDER BY mae ASC) as mae_rank,
    RANK() OVER (ORDER BY rmse ASC) as rmse_rank,
    ROUND((mae / (SELECT MIN(mae) FROM model_performance) - 1) * 100, 2) as pct_above_best
FROM model_performance
ORDER BY mae ASC;