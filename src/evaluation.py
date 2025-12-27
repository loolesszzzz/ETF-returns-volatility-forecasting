from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
import pandas as pd


def regression_metrics(y_true: pd.Series, y_pred: pd.Series) -> dict:
    """
    Compute MAE and RMSE for aligned series.
    """
    y_true, y_pred = y_true.align(y_pred, join="inner")

    return {
        "MAE": mean_absolute_error(y_true, y_pred),
        "RMSE": np.sqrt(mean_squared_error(y_true, y_pred)),
    }


def naive_volatility_metrics(realised_vol: pd.Series) -> dict:
    """
    Naive volatility forecast: yesterday's realised volatility.
    """
    y_true = realised_vol.iloc[1:]
    y_pred = realised_vol.shift(1).iloc[1:]

    return regression_metrics(y_true, y_pred)
