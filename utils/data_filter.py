# data_filter.py

import numpy as np
import pandas as pd
import logging

# Function for Filter step 1
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
        logging.info(" --- Filter Step 1\n"
                     f"Tracks length: {len(valid_tracks)}\n"
                     f"Total tracks: {total_tracks}\n"
                     f"Tracks removed by length filter: {total_tracks - mask_length.sum()}\n"
                     f"Tracks removed by velocity std filter: {mask_length.sum() - (mask_length & mask_std).sum()}\n"
                     f"Tracks removed by median velocity filter: {(mask_length & mask_std).sum() - len(valid_tracks)}\n"
                     f"Tracks remaining: {len(valid_tracks)}\n"
                     )

    # Filter the dataframe
    df_filtered = df[df['track'].isin(valid_tracks)].reset_index(drop=True)

    return df_filtered


# Function for Filter step 2
def filter_tracks_that_jump(df: pd.DataFrame, jump_threshold: float,
                            return_bad_df: bool = False, verbose: bool = True):
    """
    Remove tracks where ANY frame-to-frame movement exceeds a threshold.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain: ['track', 'frame', 'bb_center_lidar_x', 'bb_center_lidar_y'].

    jump_threshold : float
        Maximum allowed Euclidean jump distance between consecutive frames.

    return_bad_df : bool, optional
        If True, returns (good_df, bad_df). other returns only filtered df.

    verbose : bool, optional
        If True, print summary stats.

    Returns
    -------
    pd.DataFrame or (pd.DataFrame, pd.DataFrame)
        Filtered dataframe, and optionally a dataframe of removed tracks.
    """

    # --- Ensure sorted for correct diff ---
    df = df.sort_values(['track', 'frame'])

    # --- Compute per-frame displacement ---
    dx = df.groupby("track")["bb_center_lidar_x"].diff()
    dy = df.groupby("track")["bb_center_lidar_y"].diff()
    dz = df.groupby("track")["bb_center_lidar_z"].diff()

    # --- 3D Euclidean distance ---
    df["jump_dist"] = np.sqrt(dx ** 2 + dy ** 2 + dz ** 2)

    # --- Identify which tracks have ANY bad jump ---
    track_max_jump = df.groupby('track')["jump_dist"].max()

    good_tracks = track_max_jump[track_max_jump <= jump_threshold].index
    bad_tracks  = track_max_jump[track_max_jump > jump_threshold].index

    df_good = df[df["track"].isin(good_tracks)].copy()
    df_bad  = df[df["track"].isin(bad_tracks)].copy()

    # --- Print summary ---
    if verbose:
        logging.info(" --- Filter Step 2 - Jump Filter\n"
                     f"Threshold: {jump_threshold}\n"
                     f"Total received: {df['track'].nunique()}\n"
                     f"Good tracks: {len(good_tracks)}\n"
                     f"Bad tracks : {len(bad_tracks)}\n"
                     )

    # --- Return ---
    if return_bad_df:
        return df_good, df_bad
    return df_good


# Function for Filter step 3
def filter_tracks_by_movement(df: pd.DataFrame, yaxis_min_length: float,
                              track_column: str = 'track',
                              value_column: str = 'bb_center_lidar_y'
) -> tuple[pd.DataFrame, pd.DataFrame]:
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
    yaxis_movements = []

    for track_id, track_df in df.groupby(track_column):
        track_df = track_df.sort_values('frame')  # ensure correct order

        n = len(track_df)

        if n < 5:
            continue
        elif n < 25:  # too short, just use first and last
            y_start = track_df[value_column].iloc[2]
            y_end = track_df[value_column].iloc[-2]
        elif n < 50:  # too short, just use first and last
            y_start = track_df[value_column].iloc[4]
            y_end = track_df[value_column].iloc[-4]
        elif n <150:  # use second and second-last points
            y_start = track_df[value_column].iloc[6]
            y_end = track_df[value_column].iloc[-6] #last frames often show jumping
        else:  # use second and second-last points
            y_start = track_df[value_column].iloc[8]
            y_end = track_df[value_column].iloc[-10]

        if y_end - y_start < -yaxis_min_length:
            moving_tracks.append(track_id)
            # save per-track movement
            yaxis_mov = abs(y_end - y_start)
            yaxis_movements.append({
                track_column: track_id,
                "yaxis_movement": yaxis_mov,
            })

    filtered_df = df[df[track_column].isin(moving_tracks)]

    df_yaxis_movement = pd.DataFrame(yaxis_movements)

    # Stats
    total_tracks = df[track_column].nunique()
    kept_tracks = len(moving_tracks)
    removed_tracks = total_tracks - kept_tracks

    logging.info(' --- Filter Step 3 - Y-Axis Movement ---\n'
    f"Tracks received: {total_tracks}\n"
    f"Tracks kept (movement > {yaxis_min_length}): {kept_tracks}\n"
    f"Tracks removed: {removed_tracks}\n"
    )

    return filtered_df, df_yaxis_movement

# Function for Filter step 4
def replace_zero_velocity_with_nan(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Replace zero velocities with NaN while keeping all rows.
    """
    mask = df["velocity"] == 0
    df.loc[mask, "velocity"] = np.nan

    return df