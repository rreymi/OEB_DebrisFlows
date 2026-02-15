# plot_utils.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pathlib import Path
from matplotlib import font_manager
from matplotlib.colors import Normalize
from matplotlib.collections import LineCollection
from scipy.interpolate import interp1d
import matplotlib.cm as cm


# --- Helper Functions for all plots
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
        return lambda frame, _: ""

    # Convert to sorted arrays for fast lookup
    frames = df_time["frame"].to_numpy()
    times = df_time["time"].to_numpy()

    # Ensure frames are sorted
    sorted_idx = np.argsort(frames)
    frames = frames[sorted_idx]
    times = times[sorted_idx]

    def formatter(frame, _):
        # Find nearest frame efficiently
        idx = np.searchsorted(frames, frame)
        if idx == 0:
            nearest_idx = 0
        elif idx >= len(frames):
            nearest_idx = len(frames) - 1
        else:
            # Choose the closer of the two neighbors
            if abs(frames[idx] - frame) < abs(frames[idx - 1] - frame):
                nearest_idx = idx
            else:
                nearest_idx = idx - 1

        seconds = times[nearest_idx]
        if pd.isna(seconds):
            return ""

        minutes = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{minutes:02d}:{secs:02d}"

    return formatter


def add_time_top_axis(
    ax: plt.Axes,
    df_time: pd.DataFrame | None,
    x_label: str = "Time [MM:SS]",
    fontsize: int = 16,
):
    ax_top = ax.twiny()
    ax_top.set_xlim(ax.get_xlim())
    ax_top.set_xlabel(x_label, fontsize=fontsize)

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


def save_plot(fig, fig_name, output_dir):
    fig.tight_layout()
    output_path = Path(output_dir) / fig_name
    plt.savefig(output_path, dpi=300, bbox_inches="tight")


# --- Plot Functions for data per FRAME

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
def plot_variable_against_frame(df_mova: pd.DataFrame, config,
                                plot_variable, statistic,
                                color_ma: str, label_name: str, y_label: str,
                                df_time: pd.DataFrame | None = None,
                                y_lim: tuple = None,
) -> None:
    """
    Plot a per-frame variable (velocity, grainsize, or tracks) against frame number,
    and top x-axis showing time in MM:SS.

    Parameters:
        df_mova (pd.DataFrame): Dataframe with per-frame stats and 'time' column
        config
        plot_variable (str): 'velocity', 'grainsize', or 'tracks'
        statistic (str): 'mean' or 'median' (ignored for tracks)
        color_ma (str): color of Moving Average
        label_name (str): clear label name
        y_label (str): y_label
        y_lim (tuple): y_lim
        df_time (pd.DataFrame, optional): DataFrame with 'frame' and 'time' columns
    """
    # Config Values
    start_frame = config.START_FRAME
    end_frame = config.END_FRAME

    # Get columns for raw values and moving average
    raw_col, ma_col = get_plot_columns(plot_variable, statistic)

    # --- Start plotting
    fig, ax = plt.subplots(figsize=config.FIG_SIZE)

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
    fig_name = f"{statistic.capitalize()}_{plot_variable}_per_frame_{start_frame}_{end_frame}.jpeg"
    save_plot(fig, fig_name, config.OUTPUT_DIR)


def plot_piv_and_mean_velocity_per_frame(
    df_piv_mova: pd.DataFrame,
    df_mova: pd.DataFrame,
    df_time: pd.DataFrame,
    config,
) -> None:
    """
    Plot PIV and tracking velocities with lower x-axis as frame numbers
    and top x-axis as corresponding time in MM:SS.
    """

    # Config Values
    start_frame = config.START_FRAME
    end_frame = config.END_FRAME

    # --- Create figure and axes ---
    fig, ax = plt.subplots(figsize=config.FIG_SIZE)

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
                    ylim=config.YLIM_VELOCITY,
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

    # save plot
    fig_name = f"PIV_and_mean_Velocity_per_frame_{config.EVENT}_{start_frame}_{end_frame}.jpeg"
    save_plot(fig, fig_name, config.OUTPUT_DIR)


# --- Function for plotting per Track data ---

# --- XY Track path movement ---
def plot_xy_mov_tracks(df: pd.DataFrame, config,
                    x_lim: tuple[float, float] = (-10, 6),
                    y_lim: tuple[float, float] = (-8, 8),
                    ):

    """
    Plot all tracks from df whose track ID is in bad_tracks.
    """
    # Config Values
    output_dir = config.OUTPUT_DIR
    title = f'xy_track_path_mov_{config.EVENT}_{config.START_FRAME}_{config.END_FRAME}'


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



def plot_xy_mov_tracks_color_vel(
    df: pd.DataFrame, config,
    line_width: float = 1,
    cmap_name: str = "viridis",
    alpha_line: float = 0.75,
    interp_points: int = 100
):
    """
    Plot tracks as smooth continuous lines colored by velocity.
    Small line segments are interpolated to make the line visually smooth.
    """

    fig, ax = plt.subplots(figsize=(10, 10))
    cmap = cm.get_cmap(cmap_name)

    for tid, df_track in df.groupby("track"):

        df_track = df_track.iloc[::3]

        x = df_track["bb_center_lidar_x"].values
        y = df_track["bb_center_lidar_y"].values
        v = df_track["velocity"].values
        if len(x) < 2:
            continue
        # Interpolate to more points for smoothness
        t = np.linspace(0, 1, len(x))
        t_new = np.linspace(0, 1, interp_points)


        x_smooth = interp1d(t, x, kind='cubic' if len(df_track) >= 5 else 'linear')(t_new) # short tracks are interpolated linear
        y_smooth = interp1d(t, y, kind='cubic' if len(df_track) >= 5 else 'linear')(t_new)
        v_smooth = interp1d(t, v, kind='linear')(t_new)  # velocity linear

        # Create segments for gradient coloring
        points = np.array([x_smooth, y_smooth]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)

        lc = LineCollection(segments, array=v_smooth[1:], cmap=cmap,
                            linewidth=line_width, alpha=alpha_line)
        ax.add_collection(lc)

    # Axis formatting
    style_main_axis(ax,
                    xlim=config.X_LIM_AXIS,
                    ylim=config.Y_LIM_AXIS,
                    xlabel = "X (LiDAR bbox center) (m)",
                    ylabel="Y (LiDAR bbox center) (m)",
                    fontsize= 14)

    ax.set_aspect("equal", "box")
    ax.grid(True, linestyle="--", alpha=0.25)

    # Colorbar
    norm = plt.Normalize(vmin=0, vmax=df["velocity"].quantile(0.98))

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    cbar = fig.colorbar(sm, ax=ax, shrink=0.8)
    cbar.set_label("Velocity [m/s]", fontsize=13)
    cbar.ax.tick_params(labelsize=12)


    fig_name = f'xy_track_path_mov_colored_{config.EVENT}_{config.START_FRAME}_{config.END_FRAME}.jpeg'
    save_plot(fig,fig_name,config.OUTPUT_DIR)


# --- Per Track Velocity smoothed with LOWESS / Surges segmented
def plot_track_velocities_lowess(
    df_per_track_statistic: pd.DataFrame,
    df_lowess: pd.DataFrame,
    df_piv_mova: pd.DataFrame,
    df_time: pd.DataFrame, config,
) -> None:

    # Config Values
    stat_type = config.STATISTIC_TYPE
    start_frame = config.START_FRAME
    end_frame = config.END_FRAME


    # Choose statistic
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
    fig, ax = plt.subplots(figsize=config.FIG_SIZE)

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

    # LOWESS Track Velocity is plotted in segments --> avoid interpolation over large gaps
    for i, (_, seg) in enumerate(df_lowess.groupby("segment")):
        ax.plot(
            seg['frame'],
            seg[lowess_track_velocity],
            label=label_smooth if i == 0 else None,  # label only once
            color='tab:blue',
            linewidth=2.2,
            alpha=1.0,
            zorder=3
        )

    # PIV velocity for comparison
    ax.plot(
        df_piv_mova['frame'],
        df_piv_mova['piv_vel_smoothed'],
        label="PIV surface velocity smoothed",
        color='tab:red',
        linewidth=1.3,
        alpha=0.85,
        zorder=2
    )

    # --- X and Y Axis
    style_main_axis(ax,
                    xlabel="Frame Number",
                    ylabel="Velocity (m/s)",
                    xlim=(start_frame, end_frame),
                    ylim=config.YLIM_VELOCITY,
                    fontsize=16)

    # --- TOP axis (time in MM:SS)
    add_time_top_axis(ax, df_time)

    # --- Legend
    add_standard_legend(ax)

    # --- Save
    fig_name = f"PIV_and_{stat_type}_Track_velocities_{config.EVENT}_{start_frame}_{end_frame}.jpeg"
    save_plot(fig, fig_name, config.OUTPUT_DIR)


# Per Track Grainsize
def plot_track_grainsize_lowess(
    df_per_track_grainsize: pd.DataFrame,
    df_grainsize_lowess: pd.DataFrame,
    df_time: pd.DataFrame, config,
) -> None:

    # Config Values
    start_frame = config.START_FRAME
    end_frame = config.END_FRAME


    fig, ax = plt.subplots(figsize=config.FIG_SIZE)

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

    # --- X and Y Axis
    style_main_axis(ax,
                    xlabel="Frame Number",
                    ylabel="Grain Size (m)",
                    xlim=(start_frame, end_frame),
                    ylim=config.YLIM_GRAINSIZE,
                    fontsize=16)

    # --- TOP axis (time in MM:SS)
    add_time_top_axis(ax, df_time)

    # --- Legend
    add_standard_legend(ax)

    # --- Save
    fig_name = f"Track_grainsize_{config.EVENT}_{start_frame}_{end_frame}.jpeg"
    save_plot(fig, fig_name, config.OUTPUT_DIR)


# --- bubble plot ---
def plot_track_grainsize_bubble(
    df_per_track_grainsize: pd.DataFrame,
    df_per_track_velocities: pd.DataFrame,
    df_velocities_lowess: pd.DataFrame,
    df_time: pd.DataFrame, config
) -> None:

    # Config Values
    event = config.EVENT
    output_dir = config.OUTPUT_DIR
    start_frame = config.START_FRAME
    end_frame = config.END_FRAME
    ylim_velocity = config.YLIM_VELOCITY

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
    # scaled marker sizes
    # ------------------------------------------------------------------
    n = df_bin["n_tracks"]
    n_log = np.log10(n)
    n_norm = (n_log - n_log.min()) / (n_log.max() - n_log.min())
    sizes = 15 + n_norm * 120                           # size scaling

    # ------------------------------------------------------------------
    # Color marker - grain size depended
    # ------------------------------------------------------------------
    # g_log = np.log10(g + 1e-6)                        # log scaled grain size
    g_norm = (g - g.min()) / (g.max() - g.min())        # normalize grain sizes from 0 to 1, for scaling
    v_min = g.min()                                     # Compute min and percentile
    v_max = float(np.percentile(g, 98))              # percentile

    # ------------------------------------------------------------------
    # Plots
    # ------------------------------------------------------------------
    sc = ax.scatter(
        x,
        y,
        s=sizes,
        c=g_norm,
        cmap="rainbow",
        alpha=0.90,
        edgecolors="none",
        label=f"Median track velocity (binned over {frame_bin} frames)",
        vmin=v_min,
        vmax=v_max,
        zorder=1
    )

    # LOWESS Track Velocity is plotted in segments --> avoid interpolation over large gaps
    for i, (_, seg) in enumerate(df_velocities_lowess.groupby("segment")):
        ax.plot(
            seg['frame'],
            seg["lowess_mean_track_velocity"],
            label="Smoothed track velocities (LOWESS)" if i == 0 else None,  # label only once
            c="tab:grey",
            linewidth=2.2,
            alpha=0.80,
            zorder=2
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
    add_standard_legend(ax, fontsize= 14, loc='best')

    # save
    fig_name = f"GrainSize_bubble_plot_{event}_{start_frame}_{end_frame}.jpeg"
    save_plot(fig, fig_name, output_dir)


# --- Cross-section Plots
def plot_cross_section_velocity(df_clean: pd.DataFrame, config) -> None:

    # Config Values
    start_frame = config.START_FRAME
    end_frame = config.END_FRAME
    y_axis_start = config.Y_AXIS_START
    y_axis_end = config.Y_AXIS_END


    # Filter DF with mask
    mask = (
            df_clean['frame'].between(start_frame, end_frame)
            & df_clean["bb_center_lidar_y"].between(y_axis_end, y_axis_start)
    )
    df = df_clean[mask]

    # Calculate Track Velocities in predefined y-axis range
    df = (
        df.groupby("track")
        .agg(
            mean_track_velocity=("velocity", "mean"),
            mean_x_axis_pos=("bb_center_lidar_x", "mean"),
            mean_time=('time', 'mean')
        )
    )

    t_min = df["mean_time"].min()
    t_max = df["mean_time"].max()

    norm = Normalize(vmin=0, vmax=t_max - t_min)

    df['mean_time'] = df['mean_time'] - t_min

    fig, ax = plt.subplots(figsize=(16, 7))

    sc = ax.scatter(
        df['mean_x_axis_pos'],
        df['mean_track_velocity'],
        label="Mean velocity per track",
        c=df['mean_time'],
        norm=norm,  # color by mean time
        cmap='plasma',  # 'viridis'
        s=18,
        alpha=0.85,
        edgecolors="none",
        rasterized=True
    )

    style_main_axis(
        ax,
        xlabel='X-axis - cross section (m)',
        ylabel='Velocity (m/s)',
        xlim=config.X_LIM_AXIS_CS,
        ylim=config.YLIM_VELOCITY
    )

    # Add colorbar
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label("Mean Time (s)")

    # Legend
    add_standard_legend(ax)

    # save
    fig_name = f"Cross_section_velocity_{config.EVENT}_{start_frame}_{end_frame}.jpeg"
    save_plot(fig, fig_name, config.OUTPUT_DIR)
