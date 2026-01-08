# data_utils.py

import numpy as np
import pandas as pd
from pathlib import Path


def extract_frame_time_table(
    df: pd.DataFrame,
    frame_col: str = "frame",
    time_col: str = "time"
) -> pd.DataFrame:

    df_time = (
        df[[frame_col, time_col]]
        .dropna()
        .drop_duplicates(subset=frame_col)
        .sort_values(frame_col)
        .reset_index(drop=True)
    )
    return df_time


def compute_mean_median_per_frame(
    df_raw: pd.DataFrame,
    columns: list = None,
    ) -> pd.DataFrame:
    """
    Reduce dataframe to essential columns and compute per-frame statistics.
    """

    if columns is None:
        columns = ['frame', 'track', 'velocity', 'grainsize', 'time']

    # Reduce size by keeping only essential columns
    df = df_raw[columns].copy()

    # --- PER-FRAME STATISTICS ---
    df['mean_velocity_per_frame'] = df.groupby('frame')['velocity'].transform('mean')
    df['mean_grainsize_per_frame'] = df.groupby('frame')['grainsize'].transform('mean')
    df['median_velocity_per_frame'] = df.groupby('frame')['velocity'].transform('median')
    df['median_grainsize_per_frame'] = df.groupby('frame')['grainsize'].transform('median')
    df['unique_tracks_per_frame'] = df.groupby('frame')['track'].transform('nunique') # each row becomes result of nun

    return df



def load_and_merge_event_data(event: str, base_dir: str = "input_data") -> pd.DataFrame:
    """
    Load raw stats and time column for a given event, merge them, and return the dataframe.

    Parameters:
        event (str): Name of the event folder.
        base_dir (str): Base folder containing the event subfolders. Default: '01_Input_DATA'

    Returns:
        pd.DataFrame: Merged dataframe.
    """
    event_dir = Path(base_dir) / event

    # Read files
    df_raw = pd.read_csv(event_dir / f"all_stats_{event}.txt")
    time_column = pd.read_csv(event_dir / f"time_column_{event}.txt")

    # Merge on frame columns
    df_merged = df_raw.merge(time_column, left_on="frame", right_on="frame_img", how="left")

    # Drop redundant column
    df_merged = df_merged.drop(columns="frame_img")

    return df_merged


def summarize_df(df):
    """
    Prints basic summary information about a dataframe
    containing 'frame' and 'track' columns.
    """
    # --- Frame stats ---
    n_frames = df['frame'].nunique()
    min_frame = df['frame'].min()
    max_frame = df['frame'].max()
    print('Number of img frames in dataframe:', n_frames)
    print('Start at img frame number:', min_frame)
    print('End at img frame number:', max_frame)

    # --- Track stats ---
    unique_ids = df['track'].nunique()
    min_id = df['track'].min()
    max_id = df['track'].max()
    print("\nUnique Track IDs in dataframe:", unique_ids)
    print('Start ID:', min_id)
    print('End ID:', max_id)



def load_piv_data(event: str) -> pd.DataFrame:
    """
    Load PIV Data of ronny and interpolate with object detection analysis data.

    Events_Ronny: PIV_VEL_TAB2024_06_14.csv




        pd.DataFrame: Merged dataframe.
    """
    def time_to_seconds(t: str) -> float:
        parts = t.split(":")
        sec = 0.0
        for p in parts:
            sec = sec * 60 + float(p)
        return sec


    # Load PIV Data
    event_dir = Path('input_data') / 'Events_Ronny' / event / '01_Velocity'
    df_piv = pd.read_csv(event_dir / f"PIV_VEL_TAB{event}.csv")

    df_piv['time_sec'] = df_piv['Time'].apply(time_to_seconds)

    return df_piv


def merge_piv_and_tracking(df_piv: pd.DataFrame, df_mova: pd.DataFrame) -> pd.DataFrame:
    """
    Merge PIV and Tracking data on a common time axis by interpolation.

    Parameters
    ----------
    df_piv : pd.DataFrame
        PIV data. Must contain columns: 'time_sec', 'vel_un_smoothed', 'vel_smoothed'.
    df_mova : pd.DataFrame
        Tracking data. Must contain columns: 'time', 'mean_velocity_per_frame', 'mean_vel_ma'.

    Returns
    -------
    pd.DataFrame
        Merged DataFrame with interpolated values for both datasets on the common time axis.
    """
    # --- Safety checks ---
    required_piv_cols = ['time_sec', 'vel_un_smoothed', 'vel_smoothed']
    required_mova_cols = ['time', 'mean_velocity_per_frame', 'mean_vel_ma']

    if not all(col in df_piv.columns for col in required_piv_cols):
        raise ValueError(f"df_piv must contain columns: {required_piv_cols}")
    if not all(col in df_mova.columns for col in required_mova_cols):
        raise ValueError(f"df_mova must contain columns: {required_mova_cols}")


    # --- Determine common time range ---
    t_start = max(df_piv.time_sec.min(), df_mova.time.min())
    t_end   = min(df_piv.time_sec.max(), df_mova.time.max())

    if t_start >= t_end:
        raise ValueError("No overlapping time range between df_piv and df_mova")

    dt = 0.1
    t_common = np.arange(t_start, t_end + 1e-6, dt)

    # --- Helper for interpolation ---
    def interp_series(time, values):
        return np.interp(t_common, time, values)

    # --- Interpolate all series ---
    data = {
        "time_sec": t_common,
        'mova_frame': interp_series(df_mova.time, df_mova.frame),
        "mova_mean_vel_per_frame": interp_series(df_mova.time, df_mova.mean_velocity_per_frame),
        "mova_ma_vel": interp_series(df_mova.time, df_mova.mean_vel_ma),
        "piv_vel_un_smoothed": interp_series(df_piv.time_sec, df_piv.vel_un_smoothed),
        "piv_vel_smoothed": interp_series(df_piv.time_sec, df_piv.vel_smoothed)
    }

    df_merged = pd.DataFrame(data)

    return df_merged


def compute_track_velocities(
    df_filtered: pd.DataFrame,
    columns: list = None,
    ) -> pd.DataFrame:

    if columns is None:
        columns = ['frame', 'track', 'velocity', 'time']

    # Reduce size by keeping only essential columns
    df = df_filtered[columns].copy()

    mean_vel = (
        df.groupby("track")["velocity"]
          .mean()
          .rename("mean_track_velocity")
    )

    median_vel = (
        df.groupby("track")["velocity"]
          .median()
          .rename("median_track_velocity")
    )

    # 2) Center frame per track
    # index within each track
    idx = df.groupby("track").cumcount()
    sizes = df.groupby("track")["frame"].transform("size")
    center_mask = idx == (sizes  // 2)

    center_frame = (
        df.loc[center_mask, ["track", "frame"]]
          .set_index("track")["frame"]
          .rename("center_frame")
    )

    # 3) Combine
    result = (
        pd.concat([center_frame, mean_vel, median_vel], axis=1)
          .reset_index()
          .sort_values("center_frame")
    )

    return result
