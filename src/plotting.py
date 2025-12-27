import matplotlib.pyplot as plt

def plot_series(series_dict, title=None, figsize=(10, 4)):
    fig, ax = plt.subplots(figsize=figsize)

    for label, series in series_dict.items():
        ax.plot(series, label=label)

    ax.legend()
    ax.set_title(title)

    return fig, ax
