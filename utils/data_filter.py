# data_filter.py

import pandas as pd


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


def compute_mean_median_per_frame(df_raw: pd.DataFrame, columns: list = None) -> pd.DataFrame:
    """
    Reduce dataframe to essential columns and compute per-frame statistics.

    Parameters:
        df_raw (pd.DataFrame): Input raw dataframe with at least 'frame', 'track', 'velocity', 'grainsize', 'time'.
        columns (list, optional): List of essential columns to keep. Default ['frame', 'track', 'velocity', 'grainsize', 'time'].

    Returns:
        pd.DataFrame: Reduced dataframe with per-frame statistics added.
    """
    if columns is None:
        columns = ['frame', 'track', 'velocity', 'grainsize', 'time']

    # Reduce size by keeping only essential columns
    df = df_raw[columns].copy()

    # Compute per-frame statistics
    df['mean_velocity_per_frame'] = df.groupby('frame')['velocity'].transform('mean')
    df['mean_grainsize_per_frame'] = df.groupby('frame')['grainsize'].transform('mean')
    df['median_velocity_per_frame'] = df.groupby('frame')['velocity'].transform('median')
    df['median_grainsize_per_frame'] = df.groupby('frame')['grainsize'].transform('median')
    df['unique_tracks_per_frame'] = df.groupby('frame')['track'].transform('nunique')

    return df

