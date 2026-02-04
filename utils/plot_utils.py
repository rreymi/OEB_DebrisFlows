# plot_utils.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pathlib import Path
from matplotlib import font_manager

# Helper Functions for all plots
def style_main_axis(
    ax: plt.Axes,
    xlabel: str = 'Frame Number',
    ylabel: str = '',
    xlim: tuple | None = None,
    ylim: tuple | None = None,
    fontsize: int = 16,
):
    ax.set_xlabel(xlabel, fontsize=fontsize)
    ax.set_ylabel(ylabel, fontsize=fontsize)

    if xlim is not None:
        ax.set_xlim(*xlim)
    if ylim is not None:
        ax.set_ylim(*ylim)

    ax.tick_params(axis="both", labelsize=fontsize - 1, pad=8, length=4, width=1)
    ax.grid(True, linestyle="-", alpha=0.4)

def make_frame_to_mmss_formatter(df_time: pd.DataFrame | None):
    if df_time is None or df_time.empty:
        return lambda frame, pos=None: ""

    frame_to_time = dict(zip(df_time["frame"], df_time["time"]))

    def formatter(frame, pos=None):
        nearest_frame = min(frame_to_time.keys(), key=lambda f: abs(f - frame))
        seconds = frame_to_time[nearest_frame]

        if pd.isna(seconds):
            return ""

        minutes = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{minutes:02d}:{secs:02d}"

    return formatter

def add_time_top_axis(
    ax: plt.Axes,
    df_time: pd.DataFrame | None,
    xlabel: str = "Time [MM:SS]",
    fontsize: int = 16,
):
    ax_top = ax.twiny()
    ax_top.set_xlim(ax.get_xlim())
    ax_top.set_xlabel(xlabel, fontsize=fontsize)

    formatter = make_frame_to_mmss_formatter(df_time)

    ax_top.xaxis.set_major_locator(ticker.AutoLocator())
    ax_top.xaxis.set_major_formatter(ticker.FuncFormatter(formatter))
    ax_top.tick_params(axis="x", labelsize=fontsize - 1, pad=8, length=4, width=1)

    return ax_top

def add_standard_legend(
    ax: plt.Axes,
    fontsize: int = 14,
    loc: str = "best",
):
    leg = ax.legend(
        frameon=True,
        fontsize=fontsize,
        loc=loc,
        facecolor="white",
        edgecolor="black",
    )

    # Make first line visually dominant (your usual style)
    if leg.get_lines():
        plt.setp(leg.get_lines()[0], alpha=1, linewidth=2)

    return leg


# --- Plot Functions for data per FRAME ---

# Helper
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


# Main Plot Function
def plot_variable_against_frame(df_mova: pd.DataFrame, plot_variable, statistic,
                                color_ma: str, label_name: str, y_label: str,
                                y_lim: tuple[float, float] | None = None, output_dir: Path | None = None,
                                start_frame=None, end_frame=None, fig_size: tuple[int, int] = None,
                                df_time: pd.DataFrame | None = None) -> None:
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
        fig_size (tuple, optional): figure size
        df_time (pd.DataFrame, optional): DataFrame with 'frame' and 'time' columns
    """

    # Get columns for raw values and moving average
    raw_col, ma_col = get_plot_columns(plot_variable, statistic)

    # --- Start plotting
    fig, ax = plt.subplots(figsize=fig_size)

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

    # X and Y Axis
    style_main_axis(ax,
                    ylabel=f"{y_label}",
                    xlim= (start_frame, end_frame),
                    ylim=y_lim,
                    fontsize= 16)

    # --- TOP axis (time in MM:SS)
    add_time_top_axis(ax, df_time)

    # --- Legend
    add_standard_legend(ax)

    # Save figure
    fig.tight_layout()
    fig_name = f"{statistic.capitalize()}_{plot_variable}_per_frame_{start_frame}_{end_frame}.jpeg"
    output_path = Path(output_dir) / fig_name
    plt.savefig(output_path, dpi=300, bbox_inches="tight")


def plot_piv_and_mean_velocity_per_frame(
    df_piv_mova: pd.DataFrame,
    df_mova: pd.DataFrame,
    df_time: pd.DataFrame,
    event: str,
    start_frame: int,
    end_frame: int,
    fig_size: tuple[int, int] = None,
    output_dir: Path | None = None,
    ylim_velocity: tuple[float, float] | None = None,
) -> None:
    """
    Plot PIV and tracking velocities with lower x-axis as frame numbers
    and top x-axis as corresponding time in MM:SS.

    Parameters
    ----------
    df_piv_mova : pd.DataFrame
        Must contain columns: 'mova_frame', 'time_sec', 'mova_mean_vel_per_frame', 'piv_vel_smoothed'
    df_mova : pd.DataFrame
    df_time : pd.DataFrame
    event : str
    start_frame : int
        First frame to display
    end_frame : int
        Last frame to display
    fig_size : tuple, optional
        Figure size, by default (14,7)
    output_dir : Path | None, optional
    ylim_velocity: tuple[float, float] | None, optional
    """


    # --- Create figure and axes ---
    fig, ax = plt.subplots(figsize=fig_size)

    # --- Plot velocities ---
    ax.plot(df_piv_mova['frame'],
            df_piv_mova['piv_vel_smoothed'],
            label="PIV surface velocity smoothed",
            color='tab:red',
            linewidth=1.3,
            alpha=0.85,
            zorder=2
            )

    ax.plot(df_mova['frame'],
            df_mova['mean_velocity_per_frame'],
            color='0.7',
            alpha=0.55,
            linewidth=1,
            zorder=1)

    ax.plot(df_mova['frame'],
            df_mova['mean_vel_ma'],
            label="Moving average of mean velocity per frame",
            color='tab:blue',
            linewidth=2.2,
            alpha=1.0,
            zorder=3
            )

    # X and Y Axis
    style_main_axis(ax,
                    xlabel="Frame Number",
                    ylabel="Velocity (m/s)",
                    xlim=(start_frame, end_frame),
                    ylim=ylim_velocity,
                    fontsize=16)

    # --- TOP axis (time in MM:SS)
    add_time_top_axis(ax, df_time)


    leg = ax.legend(
        title="Velocities (m/s)",
        title_fontproperties=font_manager.FontProperties(weight='bold', size=16),
        fontsize=14,
        frameon=True,
        loc="best",
        facecolor="white",
        edgecolor="black")
    plt.setp(leg.get_lines()[0], alpha=1, linewidth=2)

    fig.tight_layout()

    fig_name = f"PIV_and_mean_Velocity_per_frame_{event}_{start_frame}_{end_frame}.jpeg"
    output_path = Path(output_dir) / fig_name
    plt.savefig(output_path, dpi=300, bbox_inches="tight")


# --- Function for plotting per Track data ---

def plot_track_velocities_lowess(
    df_per_track_statistic: pd.DataFrame,
    df_lowess: pd.DataFrame,
    df_piv_mova: pd.DataFrame,
    stat_type: str,
    event: str,
    start_frame: int,
    end_frame: int,
    df_time: pd.DataFrame,
    fig_size: tuple[int, int] = None,
    output_dir: Path | None = None,
    ylim_velocity: tuple[float, float] | None = None,
) -> None:


    if stat_type == "mean":
        track_velocity = "mean_track_velocity"
        lowess_track_velocity = "lowess_mean_track_velocity"
        label_raw = "Mean velocity per track"
        label_smooth = "Smoothed track velocities (LOWESS)"
    elif stat_type == "median":
        track_velocity = "median_track_velocity"
        lowess_track_velocity = "lowess_median_track_velocity"
        label_raw = "Median velocity per track"
        label_smooth = "Smoothed track velocities (LOWESS)"
    else:
        raise ValueError("plot_type must be either 'mean' or 'median'")

    # --- Start plotting
    fig, ax = plt.subplots(figsize=fig_size)

    # Raw values
    ax.scatter(
        df_per_track_statistic["center_frame"],
        df_per_track_statistic[track_velocity],
        label=label_raw,
        s=10,  # small marker
        c="0.7",  # light gray (neutral, print-safe)
        alpha=0.45,  # faint visibility
        marker="o",  # clean filled marker
        edgecolors="none",  # no border
        linewidths=0,
        zorder=1,
        rasterized=True  # optional but recommended
    )

    ax.plot(
        df_lowess['frame'],
        df_lowess[lowess_track_velocity],
        label=label_smooth,
        color='tab:blue',
        linewidth=2.2,
        alpha=1.0,
        zorder=3
    )

    ax.plot(
        df_piv_mova['frame'],
        df_piv_mova['piv_vel_smoothed'],
        label="PIV surface velocity smoothed",
        color='tab:red',
        linewidth=1.3,
        alpha=0.85,
        zorder=2
    )

    # X and Y Axis
    style_main_axis(ax,
                    xlabel="Frame Number",
                    ylabel="Velocity (m/s)",
                    xlim=(start_frame, end_frame),
                    ylim=ylim_velocity,
                    fontsize=16)

    # --- TOP axis (time in MM:SS)
    add_time_top_axis(ax, df_time)

    # --- Legend
    add_standard_legend(ax)

    # --- Save
    fig.tight_layout()
    fig_name = f"PIV_and_{stat_type}_Track_velocities_{event}_{start_frame}_{end_frame}.jpeg"
    output_path = Path(output_dir) / fig_name
    plt.savefig(output_path, dpi=300, bbox_inches="tight")



def plot_track_grainsize_lowess(
    df_per_track_grainsize: pd.DataFrame,
    df_grainsize_lowess: pd.DataFrame,
    df_piv_mova: pd.DataFrame,
    event: str,
    start_frame: int,
    end_frame: int,
    df_time: pd.DataFrame,
    fig_size: tuple[int, int] = None,
    output_dir: Path | None = None,
    ylim_grainsize: tuple[float, float] | None = None,
) -> None:


    # --- Frame -> time mapping for top axis ---
    frame_to_time = {}
    if df_time is not None and not df_time.empty:
        # assume df_time is already cleaned and sorted
        frame_to_time = dict(zip(df_time['frame'], df_time['time']))

    # --- Function to convert frame -> MM:SS ---
    def frame_to_mmss(frame):
        if not frame_to_time:
            return ""
        nearest_frame = min(frame_to_time.keys(), key=lambda f: abs(f - frame))
        seconds = frame_to_time[nearest_frame]
        if pd.isna(seconds):
            return ""
        minutes = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{minutes:02d}:{secs:02d}"


    # --- Start plotting
    fig, ax = plt.subplots(figsize=fig_size)

    # Raw values
    ax.scatter(
        df_per_track_grainsize["center_frame"],
        df_per_track_grainsize['mean_track_grainsize'],
        label='Mean grain size per track',
        s=10,  # small marker
        c="0.7",  # light gray (neutral, print-safe)
        alpha=0.45,  # faint visibility
        marker="o",  # clean filled marker
        edgecolors="none",  # no border
        linewidths=0,
        zorder=1,
        rasterized=True  # optional but recommended
    )

    ax.plot(
        df_grainsize_lowess['frame'],
        df_grainsize_lowess['lowess_mean_track_grainsize'],
        label='Smoothed track grain sizes (LOWESS)',
        color='tab:blue',
        linewidth=2.2,
        alpha=1.0,
        zorder=3
    )

    # X and Y Axis
    style_main_axis(ax,
                    xlabel="Frame Number",
                    ylabel="Grain Size (m)",
                    xlim=(start_frame, end_frame),
                    ylim=ylim_grainsize,
                    fontsize=16)

    # --- TOP axis (time in MM:SS)
    ax_top = ax.twiny()
    ax_top.set_xlim(ax.get_xlim())
    ax_top.set_xlabel("Time [MM:SS]", fontsize=16)

    # Set tick locations and formatting
    ax_top.xaxis.set_major_locator(ticker.AutoLocator())
    ax_top.xaxis.set_major_formatter(ticker.FuncFormatter(lambda val, pos: frame_to_mmss(val)))
    ax_top.tick_params(axis='x', labelsize=15, pad=8, length=4, width=1)

    # Legend
    leg = ax.legend(frameon=True, fontsize=16, loc="best", facecolor="white", edgecolor="black")
    plt.setp(leg.get_lines()[0], alpha=1, linewidth=2)

    fig.tight_layout()

    fig_name = f"Track_grainsize_{event}_{start_frame}_{end_frame}.jpeg"
    output_path = Path(output_dir) / fig_name
    plt.savefig(output_path, dpi=300, bbox_inches="tight")




# --- XY Track path movement ---
def plot_xy_mov_tracks(df: pd.DataFrame,
                    x_lim=(-10, 6),
                    y_lim=(-8, 8),
                    title = str,
                    output_dir: Path | None = None):
    """
    Plot all tracks from df whose track ID is in bad_tracks.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain columns ['track', 'bb_center_lidar_x', 'bb_center_lidar_y'].

    x_lim : tuple, optional
        X-axis limits.
    y_lim : tuple, optional
        Y-axis limits.
    title : str,

    output_dir : Path | None, optional
    """

    fig, ax = plt.subplots(figsize=(8, 8))

    # iterate over track IDs
    for tid, df_track in df.groupby("track"):
        ax.plot(df_track["bb_center_lidar_x"],
                df_track["bb_center_lidar_y"],
                linewidth=1)

    # formatting
    ax.set_xlim(x_lim)
    ax.set_ylim(y_lim)
    ax.set_xlabel("X (LiDAR bbox center)")
    ax.set_ylabel("Y (LiDAR bbox center)")
    ax.set_aspect("equal", "box")
    ax.grid(True, linestyle='--', alpha=0.3)

    # Save figure
    fig_name = f"{title}.jpeg"
    output_path = Path(output_dir) / fig_name
    plt.savefig(output_path, dpi=300, bbox_inches="tight")

    return output_path


# --- bubble plot ---

def plot_track_grainsize_bubble(
    df_per_track_grainsize: pd.DataFrame,
    df_per_track_velocities: pd.DataFrame,
    df_velocities_lowess: pd.DataFrame,
    event: str,
    start_frame: int,
    end_frame: int,
    df_time: pd.DataFrame,
    output_dir: Path | None = None,
    ylim_velocity: tuple[float, float] | None = None,
) -> None:

    frame_bin = 10  # BIN WIDTH (frames)

    fig, ax = plt.subplots(figsize=(16, 7))


    # ------------------------------------------------------------------
    # Filter time window
    # ------------------------------------------------------------------
    df_v = df_per_track_velocities[
        df_per_track_velocities["center_frame"].between(start_frame, end_frame)
    ].copy()

    df_g = df_per_track_grainsize[
        df_per_track_grainsize["center_frame"].between(start_frame, end_frame)
    ].copy()

    # ------------------------------------------------------------------
    # Add frame bins
    # ------------------------------------------------------------------
    df_v["frame_bin"] = (df_v["center_frame"] // frame_bin) * frame_bin
    df_g["frame_bin"] = (df_g["center_frame"] // frame_bin) * frame_bin

    # ------------------------------------------------------------------
    # Aggregate per bin
    # ------------------------------------------------------------------
    df_v_bin = (
        df_v.groupby("frame_bin")
        .agg(mean_track_velocity=("mean_track_velocity", "median"))
        .reset_index()
    )

    df_g_bin = (
        df_g.groupby("frame_bin")
        .agg(
            mean_track_grainsize=("mean_track_grainsize", "mean"),
            n_tracks=("mean_track_grainsize", "size")
        )
        .reset_index()
    )

    # ------------------------------------------------------------------
    # Merge velocity + grain size
    # ------------------------------------------------------------------
    df_bin = pd.merge(
        df_v_bin,
        df_g_bin,
        on="frame_bin",
        how="inner"
    )

    # ------------------------------------------------------------------
    # Data for plotting
    # ------------------------------------------------------------------
    x = df_bin["frame_bin"]
    y = df_bin["mean_track_velocity"]
    g = df_bin["mean_track_grainsize"]

    # ------------------------------------------------------------------
    # Log-scaled marker sizes
    # ------------------------------------------------------------------
    n = df_bin["n_tracks"]

    n_log = np.log10(n)
    n_norm = (n_log - n_log.min()) / (n_log.max() - n_log.min())

    sizes = 15 + n_norm * 120

    g = df_bin["mean_track_grainsize"]
    g_log = np.log10(g + 1e-6)
    g_norm = (g - g.min()) / (g.max() - g.min())

    # Compute 97th percentile
    vmin = g.min()
    vmax = np.percentile(g, 98)  # 95th percentile

    sc = ax.scatter(
        x,
        y,
        s=sizes,  # confidence
        c=g_norm,  # g_norm#g_log,           # grain size
        cmap="rainbow",
        alpha=0.90,
        edgecolors="none",
        label=f"Median track velocity (binned over {frame_bin} frames)",
        vmin=vmin,
        vmax=vmax,
    )

    ax.plot(
        df_velocities_lowess["frame"],
        df_velocities_lowess["lowess_mean_track_velocity"],
        c="tab:grey",
        label="Smoothed track velocities (LOWESS)",
        alpha=0.80
    )

    # --- Log ticks, normal numbers ---
    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label("Grain Size (m)", fontsize=14)
    cbar.ax.tick_params(labelsize=12, width=1.2, length=6)

    style_main_axis(ax,
                    xlabel="Frame Number",
                    xlim=(start_frame, end_frame),
                    ylabel= "Velocity (m/s)",
                    ylim= ylim_velocity,
                    fontsize= 14)

    # --- TOP axis (time in MM:SS)
    add_time_top_axis(ax, df_time)

    # --- Legend
    add_standard_legend(ax)

    # save
    fig.tight_layout()
    fig_name = f"GrainSize_bubble_plot_{event}_{start_frame}_{end_frame}.jpeg"
    output_path = Path(output_dir) / fig_name
    plt.savefig(output_path, dpi=300, bbox_inches="tight")

