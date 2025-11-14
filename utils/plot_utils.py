# plot_utils.py

import math as math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pathlib import Path


def get_plot_columns(plot_variable: str, statistic: str):
    """
    Return the column names for raw per-frame values and moving average based on user input.
    """
    plot_variable = plot_variable.lower()
    statistic = statistic.lower()

    if plot_variable == "velocity":
        if statistic == "mean":
            return "mean_velocity_per_frame", "mean_vel_ma"
        elif statistic == "median":
            return "median_velocity_per_frame", "median_vel_ma"
    elif plot_variable == "grainsize":
        if statistic == "mean":
            return "mean_grainsize_per_frame", "mean_grain_ma"
        elif statistic == "median":
            return "median_grainsize_per_frame", "median_grain_ma"
    elif plot_variable == "tracks":
        return "unique_tracks_per_frame", "tracks_ma"

    raise ValueError(f"Unknown variable/statistic combination: {plot_variable}, {statistic}")


def prepare_df_for_plot(df: pd.DataFrame, window_size: int = 9) -> pd.DataFrame:
    """
    Prepare the dataframe for plotting:
    - Remove duplicate frames
    - Sort by frame
    - Compute rolling moving averages for per-frame columns

    Parameters:
        df (pd.DataFrame): Input dataframe with per-frame statistics and 'time' column
        window_size (int): Window size for moving average

    Returns:
        pd.DataFrame: Dataframe ready for plotting with rolling averages added
    """
    # Drop duplicate frames and sort
    df_event = df.drop_duplicates(subset="frame", keep="first").copy()
    df_event = df_event.sort_values(by="frame")

    # Define columns for rolling average
    rolling_cols = {
        "mean_velocity_per_frame": "mean_vel_ma",
        "median_velocity_per_frame": "median_vel_ma",
        "mean_grainsize_per_frame": "mean_grain_ma",
        "median_grainsize_per_frame": "median_grain_ma",
        "unique_tracks_per_frame": "tracks_ma"
    }

    # Compute moving averages
    for col, ma_col in rolling_cols.items():
        if col in df_event.columns:
            df_event[ma_col] = df_event[col].rolling(window=window_size, center=True).mean()

    return df_event


def plot_variable_against_frame(df_mova: pd.DataFrame, plot_variable, statistic,
                                color_ma: str, label_name: str, y_label: str,
                                y_lim: tuple[float, float] | None = None, output_dir: Path | None = None,
                                start_frame=None, end_frame=None, show_plot=True):
    """
    Plot a per-frame variable (velocity, grainsize, or tracks) against frame number,
    and top x-axis showing time in MM:SS.

    Parameters:
        df_mova (pd.DataFrame): Dataframe with per-frame stats and 'time' column
        plot_variable (str): 'velocity', 'grainsize', or 'tracks'
        statistic (str): 'mean' or 'median' (ignored for tracks)
        color_ma (str): color of Moving Average
        label_name (str): clear label name
        y_label (str): clear y_label
        y_lim (tuple): limits of y-axis
        output_dir (str or Path): folder to save the figure
        start_frame (int, optional): start frame for x-axis
        end_frame (int, optional): end frame for x-axis
        show_plot (bool, optional): whether to call plt.show()
    """


    # Prepare dataframe
    # df_mova = prepare_df_for_plot(df, window_size=window_size)

    # Get columns for raw values and moving average
    raw_col, ma_col = get_plot_columns(plot_variable, statistic)

    # Set default frame limits if not provided
    if start_frame is None:
        start_frame = df_mova['frame'].min()
    if end_frame is None:
        end_frame = df_mova['frame'].max()

    # Start plotting
    fig, ax = plt.subplots(figsize=(14, 7))

    # Raw values
    ax.plot(
        df_mova['frame'],
        df_mova[raw_col],
        label=f"{statistic.capitalize()} {label_name} per frame",
        color="lightgray",
        alpha=0.9,
        linewidth=1
    )

    # Moving average
    ax.plot(
        df_mova['frame'],
        df_mova[ma_col],
        label="Moving average",
        color= color_ma,
        linewidth=2
    )

    # --- X axis
    ax.set_xlabel("Frame Number", fontsize=18)
    ax.set_xlim(start_frame, end_frame)

    # --- Y axis
    ax.set_ylabel(f"{y_label}", fontsize=18)
    ax.set_ylim(y_lim) # Y-axis max * 1.1 to increase dist

    ax.tick_params(axis='both', labelsize=14, pad=8, length=4, width=1)
    ax.grid(True, linestyle="-", alpha=0.5)

    # --- TOP axis (time in MM:SS)
    ax_top = ax.twiny()
    ax_top.set_xlim(ax.get_xlim())
    ax_top.set_xlabel("Time [MM:SS]", fontsize=16)

    # Function to convert frame -> MM:SS
    def frame_to_mmss(frame):
        idx = (df_mova['frame'] - frame).abs().idxmin()
        seconds = df_mova.loc[idx, 'time']
        minutes = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{minutes:02d}:{secs:02d}"

    # Set tick locations and formatting
    ax_top.xaxis.set_major_locator(ticker.AutoLocator())
    ax_top.xaxis.set_major_formatter(ticker.FuncFormatter(lambda val, pos: frame_to_mmss(val)))
    ax_top.tick_params(axis='x', labelsize=14, pad=8, length=4, width=1)


    # Legend
    leg = ax.legend(frameon=True, fontsize=16, loc="best", facecolor="white", edgecolor="black")
    plt.setp(leg.get_lines()[0], alpha=1, linewidth=2)

    fig.tight_layout()

    # Save figure
    fig_name = f"{statistic.capitalize()}_{plot_variable}_per_frame.jpeg"
    output_path = Path(output_dir) / fig_name
    plt.savefig(output_path, dpi=300, bbox_inches="tight")

    if show_plot:
        plt.show()

    return output_path