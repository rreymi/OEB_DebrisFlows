# data_filter.py

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def filter_tracks_that_jump(df: pd.DataFrame, jump_threshold: float,
                            return_bad: bool = False, verbose: bool = True):
    """
    Remove tracks where ANY frame-to-frame movement exceeds a threshold.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain: ['track', 'frame', 'bb_center_lidar_x', 'bb_center_lidar_y'].

    jump_threshold : float
        Maximum allowed Euclidean jump distance between consecutive frames.

    return_bad : bool, optional
        If True, returns (good_df, bad_df). Otherwise returns only filtered df.

    verbose : bool, optional
        If True, print summary stats.

    Returns
    -------
    pd.DataFrame or (pd.DataFrame, pd.DataFrame)
        Filtered dataframe, and optionally a dataframe of removed tracks.
    """

    # --- Ensure sorted for correct diff ---
    df = df.sort_values(['track', 'frame']).copy()

    # --- Compute per-frame displacement ---
    dx = df.groupby("track")["bb_center_lidar_x"].diff()
    dy = df.groupby("track")["bb_center_lidar_y"].diff()

    df["jump_dist"] = np.sqrt(dx**2 + dy**2)

    # --- Identify which tracks have ANY bad jump ---
    track_max_jump = df.groupby('track')["jump_dist"].max()

    good_tracks = track_max_jump[track_max_jump <= jump_threshold].index
    bad_tracks  = track_max_jump[track_max_jump > jump_threshold].index

    df_good = df[df["track"].isin(good_tracks)].copy()
    df_bad  = df[df["track"].isin(bad_tracks)].copy()

    # --- Print summary ---
    if verbose:
        print("=== Jump Filter Summary ===")
        print(f"Threshold: {jump_threshold}")
        print(f"Total tracks: {df['track'].nunique()}")
        print(f"Good tracks: {len(good_tracks)}")
        print(f"Bad tracks : {len(bad_tracks)}")
        print("===========================")

    # --- Return ---
    if return_bad:
        return df_good, df_bad
    return df_good



def plot_bad_tracks(df: pd.DataFrame,
                    bad_tracks,
                    xlim=(-10, 5),
                    ylim=(-8, 5),
                    figsize=(8, 8),
                    title="Bad Tracks"):
    """
    Plot all tracks from df whose track ID is in bad_tracks.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain columns ['track', 'bb_center_lidar_x', 'bb_center_lidar_y'].
    bad_tracks : list or array-like
        List of track IDs considered bad.
    xlim : tuple, optional
        X-axis limits.
    ylim : tuple, optional
        Y-axis limits.
    figsize : tuple, optional
        Figure size.
    title : str, optional
        Plot title.
    """

    df_bad = df[df['track'].isin(bad_tracks)]

    fig, ax = plt.subplots(figsize=figsize)

    # iterate over track IDs
    for tid, df_track in df_bad.groupby("track"):
        ax.plot(df_track["bb_center_lidar_x"],
                df_track["bb_center_lidar_y"],
                linewidth=1)

    # formatting
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_xlabel("X (LiDAR center)")
    ax.set_ylabel("Y (LiDAR center)")
    ax.set_aspect("equal", "box")
    ax.set_title(title)
    ax.grid(True, linestyle='--', alpha=0.3)

    plt.tight_layout()
    plt.show()


def filter_tracks_by_movement(df: pd.DataFrame, yaxis_min_length: float, track_column: str = 'track',
                              value_column: str = 'bb_center_lidar_y') -> pd.DataFrame:
    """
    Filter tracks in a dataframe based on the movement range of a value column.

    Parameters:
        df (pd.DataFrame): Input dataframe.
        yaxis_min_length (float): Minimum required movement range for tracks to keep.
        track_column (str): Column name containing track IDs. Default: 'track'.
        value_column (str): Column to measure movement range. Default: 'bb_center_lidar_y'.

    Returns:
        pd.DataFrame: Filtered dataframe containing only tracks with movement above the threshold.
    """
    # Calculate movement range per track
    track_ranges = df.groupby(track_column)[value_column].agg(lambda x: x.max() - x.min())

    # Identify tracks above threshold
    moving_tracks = track_ranges[track_ranges > yaxis_min_length].index

    # Filter dataframe
    filtered_df = df[df[track_column].isin(moving_tracks)]

    return filtered_df




def filter_rows_upperlimit(df: pd.DataFrame, velocity_upperlimit: float, grainsize_upperlimit: float) -> pd.DataFrame:
    """
    Filter a dataframe by upper limits for velocity and grainsize,
    and remove rows with grainsize = 0 or missing values.

    Parameters:
        df (pd.DataFrame): Input dataframe with columns 'velocity' and 'grainsize'.
        velocity_upperlimit (float): Maximum allowed velocity.
        grainsize_upperlimit (float): Maximum allowed grainsize.

    Returns:
        pd.DataFrame: Filtered dataframe.
    """
    filtered_df = df[
        (df['grainsize'] != 0) &
        (df['velocity'] <= velocity_upperlimit) &
        (df['grainsize'] <= grainsize_upperlimit)
        ].dropna(subset=['velocity', 'grainsize'])

    return filtered_df
