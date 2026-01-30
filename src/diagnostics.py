# src/diagnostics.py

import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import acf
from statsmodels.stats.diagnostic import acorr_ljungbox


def _prepare_residuals(residuals):
    """
    Ensure residuals are a clean pandas Series with no NaNs.
    """
    if not isinstance(residuals, pd.Series):
        residuals = pd.Series(residuals)

    res = residuals.dropna()

    if len(res) < 5:
        raise ValueError("Too few residuals for diagnostics after cleaning.")

    return res


def plot_residuals(residuals, title="Model Residuals"):
    res = _prepare_residuals(residuals)

    plt.figure(figsize=(10, 4))
    plt.plot(res)
    plt.title(title)
    plt.tight_layout()
    plt.show()


def plot_residual_acf(residuals, nlags=30, title="ACF of Residuals"):
    res = _prepare_residuals(residuals)

    max_lags = min(nlags, len(res) - 1)

    plt.figure(figsize=(10, 4))
    plt.stem(acf(res, nlags=max_lags))
    plt.title(title)
    plt.tight_layout()
    plt.show()


def ljung_box_test(residuals, lags=(10, 20)):
    res = _prepare_residuals(residuals)

    max_lag = max(lags)
    if len(res) <= max_lag:
        raise ValueError(
            f"Not enough residuals for Ljung–Box test. "
            f"Need > {max_lag}, got {len(res)}."
        )

    return acorr_ljungbox(
        res,
        lags=list(lags),
        return_df=True
    )
