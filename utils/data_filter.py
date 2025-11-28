# data_filter.py

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import pandas as pd

def filter_tracks(
    df: pd.DataFrame,
    min_track_length: int,
    max_track_length: int,
    max_std_track_vel: float,
    min_median_track_vel: float,
    verbose: bool = True
) -> pd.DataFrame:
    # Compute track-level stats
    track_stats = df.groupby('track').agg(
        track_length=('track', 'size'),
        track_vel_std=('velocity', 'std'),
        track_vel_median=('velocity', 'median')
    )

    # Handle NaN std (tracks with only 1 row)
    track_stats['track_vel_std'] = track_stats['track_vel_std'].fillna(0)

    # Total tracks before filtering
    total_tracks = len(track_stats)

    # Apply filters step by step
    mask_length = (track_stats['track_length'] >= min_track_length) & \
                  (track_stats['track_length'] <= max_track_length)
    mask_std    = (track_stats['track_vel_std'] <= max_std_track_vel)
    mask_median = (track_stats['track_vel_median'] >= min_median_track_vel)

    # Combine all filters
    valid_tracks = track_stats[mask_length & mask_std & mask_median].index

    # Debug / verbose output
    if verbose:
        print(f"Total tracks: {total_tracks}")
        print(f"Tracks removed by length filter: {total_tracks - mask_length.sum()}")
        print(f"Tracks removed by velocity std filter: {mask_length.sum() - (mask_length & mask_std).sum()}")
        print(f"Tracks removed by median velocity filter: {(mask_length & mask_std).sum() - len(valid_tracks)}")
        print(f"Tracks remaining: {len(valid_tracks)}")

    # Filter the dataframe
    df_filtered = df[df['track'].isin(valid_tracks)].reset_index(drop=True)

    return df_filtered





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




def filter_tracks_by_movement(df: pd.DataFrame, yaxis_min_length: float,
                              track_column: str = 'track',
                              value_column: str = 'bb_center_lidar_y') -> pd.DataFrame:
    """
    Filter tracks based on start vs end displacement (ignoring outliers).

    Uses the second and second-last points to avoid spurious extremes.

    Parameters:
        df (pd.DataFrame): Input dataframe.
        yaxis_min_length (float): Minimum required movement to keep track.
        track_column (str): Column name for track IDs.
        value_column (str): Column to measure movement.

    Returns:
        pd.DataFrame: Filtered dataframe with moving tracks only.
    """
    moving_tracks = []

    for track_id, track_df in df.groupby(track_column):
        track_df = track_df.sort_values('frame')  # ensure correct order

        n = len(track_df)

        if n < 4:
            continue
        elif n < 25:  # too short, just use first and last
            y_start = track_df[value_column].iloc[2]
            y_end = track_df[value_column].iloc[-2]
        elif n < 50:  # too short, just use first and last
            y_start = track_df[value_column].iloc[4]
            y_end = track_df[value_column].iloc[-4]
        elif n <150:  # use second and second-last points
            y_start = track_df[value_column].iloc[6]
            y_end = track_df[value_column].iloc[-6] #da die letzten frames oft verzerrt sind
        else:  # use second and second-last points
            y_start = track_df[value_column].iloc[8]
            y_end = track_df[value_column].iloc[-10] #da die letzten frames oft verzerrt sind

        if abs(y_end - y_start) > yaxis_min_length:
            moving_tracks.append(track_id)

    return df[df[track_column].isin(moving_tracks)]

def filter_rows_nonzero_velocity(
    df: pd.DataFrame,
    verbose: bool = True
) -> pd.DataFrame:
    """
    Remove rows with zero velocity.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe containing a 'velocity' column.
    verbose : bool, optional
        Print debug information, by default True.

    Returns
    -------
    pd.DataFrame
        DataFrame with rows where velocity == 0 removed.
    """
    mask = df['velocity'] != 0

    if verbose:
        removed = (~mask).sum()
        kept = mask.sum()
        print(f"Removed {removed} rows with velocity == 0")
        print(f"Kept {kept} rows")

    return df.loc[mask].reset_index(drop=True)


'''
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
        (df['velocity'] != 0) &
        (df['grainsize'] != 0) &
        (df['velocity'] <= velocity_upperlimit) &
        (df['grainsize'] <= grainsize_upperlimit)
        ].dropna(subset=['velocity', 'grainsize'])

    return filtered_df
'''



def clean_frames_low_detections(df: pd.DataFrame, min_num_detections: int = 10) -> pd.DataFrame:
    """
    Set frame statistics to zero if the number of unique tracks
    is below the minimum threshold.
    """

    cols_to_zero = [
        "mean_vel_ma",
        "mean_grain_ma",
    ]

    mask = df["unique_tracks_per_frame"] <= min_num_detections

    df.loc[mask, cols_to_zero] = 0

    return df