import pandas as pd


# ======================
# Core processed data
# ======================

def load_returns(path="../data/processed/daily_returns.csv"):
    """
    Load cleaned daily log returns.
    """
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df.index)
    return df.sort_index()


def load_realised_vol(path="../data/processed/realised_volatility_21d.csv"):
    """
    Load 21-day realised volatility series.
    """
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df.index)
    return df.sort_index()


# ======================
# Model evaluation outputs
# ======================

def load_return_results(
    path="../outputs/tables/return_model_comparison.csv"
):
    """
    Load return model comparison table (MAE / RMSE).
    """
    return pd.read_csv(path)


def load_volatility_results(
    path="../outputs/tables/volatility_model_comparison.csv"
):
    """
    Load volatility model comparison table (MAE / RMSE).
    """
    return pd.read_csv(path)

# ======================
# Forecast outputs
# ======================

def load_forecast(path):
    """
    Load a forecast series with datetime index.
    """
    s = pd.read_csv(path, index_col=0, parse_dates=True).squeeze()
    s.index = pd.to_datetime(s.index)
    return s.sort_index()


def align_volatility_series(*series):
    """
    Align multiple volatility series on their common index.
    Returns aligned series in the same order.
    """
    common_index = series[0].index
    for s in series[1:]:
        common_index = common_index.intersection(s.index)

    return [s.loc[common_index] for s in series]
