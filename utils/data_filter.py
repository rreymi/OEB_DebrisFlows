# data_filter.py

import numpy as np
import pandas as pd
import logging

# FILTER AND SMOOTHING DATA

# Step 1 - Remove clear OUTLIERS and replace zeros with NANS
def filter_tracks_range(
    df: pd.DataFrame,
    vel_range: tuple,
    gs_range: tuple,
) -> pd.DataFrame:

    df = df.copy()

    # Physical range filtering
    df["velocity"] = df["velocity"].where(
        df["velocity"].between(*vel_range), np.nan
    )
    df["grainsize"] = df["grainsize"].where(
        df["grainsize"].between(*gs_range), np.nan
    )

    # Replace zeros with NaN
    df[["velocity", "grainsize"]] = df[["velocity", "grainsize"]].replace(0, np.nan)

    return df


# Step 2 - Rolling MEDIAN Filter to remove spikes/artifacts in DATA
def rolling_median_filter(
    df: pd.DataFrame,
    min_window: int,
    max_window: int,
) -> pd.DataFrame:

    # Store filtered series per track, keeping original indices
    filtered_velocity: list[pd.Series] = []
    filtered_grainsize: list[pd.Series] = []

    for track_id, track in df.groupby('track', sort=False):
        # Adaptive window: 1/5 of track length, min 3, max 11
        window = max(min_window, min(max_window, len(track) // 5))
        if window % 2 == 0:
            window += 1

        # Compute rolling median
        vel_filtered  = track['velocity'].rolling(
            window=window, center=True, min_periods=3
        ).median()
        vel_filtered .index = track.index
        filtered_velocity.append(vel_filtered )

        gs_filtered = track['grainsize'].rolling(
            window=window, center=True,min_periods=3
        ).median()
        gs_filtered.index = track.index
        filtered_grainsize.append(gs_filtered)

    # Assign back to original df (aligned by index)
    df['velocity_median_filtered'] = pd.concat(filtered_velocity).sort_index()
    df['grainsize_median_filtered'] = pd.concat(filtered_grainsize).sort_index()

    return df


# Step 3 - FILTER out TrackIDS that have a small Y-AXIS movement
def filter_tracks_by_movement(df: pd.DataFrame, yaxis_min_length: float,
                              track_column: str = 'track',
                              value_column: str = 'bb_center_lidar_y'
) -> pd.DataFrame:

    moving_tracks = []

    for track_id, track_df in df.groupby(track_column):
        track_df = track_df.sort_values('frame')  # ensure correct order

        n = len(track_df)

        if n < 20:
            y_start1 = track_df[value_column].iloc[1]
            y_end1 = track_df[value_column].iloc[-1]
            diff1 = y_end1 - y_start1
            y_start2 = track_df[value_column].iloc[2]
            y_end2 = track_df[value_column].iloc[-2]
            diff2 = y_end2 - y_start2

            if (diff1 < -yaxis_min_length) and (diff2 < -yaxis_min_length):
                moving_tracks.append(track_id)

        else:
            y_start = track_df[value_column].iloc[:5].median()
            y_end = track_df[value_column].iloc[-5:].median()
            diff = y_end - y_start

            if diff < -yaxis_min_length:
                moving_tracks.append(track_id)

    filtered_df = df[df[track_column].isin(moving_tracks)]

    # Stats
    total_tracks = df[track_column].nunique()
    kept_tracks = len(moving_tracks)
    removed_tracks = total_tracks - kept_tracks

    logging.info(' --- 1. Filter Step - Y-Axis Movement ---\n'
    f"Number of Track IDs: {total_tracks}\n"
    f"Tracks kept (movement > {yaxis_min_length}): {kept_tracks}\n"
    f"Tracks removed: {removed_tracks}\n"
    )

    return filtered_df

# Step 4 - Filter out tracks that jump
def filter_tracks_that_jump(
        df: pd.DataFrame,
        jump_threshold: float,
) -> tuple[pd.DataFrame,pd.DataFrame]:

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
    logging.info(" --- Filter Step 2 - Jump Filter\n"
                 f"Threshold: {jump_threshold}\n"
                 f"Total received: {df['track'].nunique()}\n"
                 f"Good tracks: {len(good_tracks)}\n"
                 f"Bad tracks : {len(bad_tracks)}\n"
                 )
    return df_good, df_bad


# Step 5 - Filter out track that move very slow
def filter_tracks_by_stats(
    df: pd.DataFrame,
    min_median_track_vel: float,
) -> pd.DataFrame:

    track_stats = df.groupby('track').agg(
        track_vel_median=('velocity_median_filtered', 'median'))

    total_tracks = len(track_stats)

    mask_vel_median = (track_stats['track_vel_median'] >= min_median_track_vel)

    # Combine all filters
    valid_tracks = track_stats[mask_vel_median].index

    # Debug / verbose output
    logging.info(
        " --- 2. Filter Step - very slow tracks \n"
        f"Total tracks: {total_tracks}\n"
        f"Tracks removed by min track median velocity filter: {total_tracks - mask_vel_median.sum()} \n"
        f"Tracks remaining: {len(valid_tracks)}\n"
    )

    # Filter the dataframe
    df_filtered = df[df['track'].isin(valid_tracks)].reset_index(drop=True)

    return df_filtered