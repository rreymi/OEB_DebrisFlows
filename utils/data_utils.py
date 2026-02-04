# data_utils.py

import numpy as np
import pandas as pd
from pathlib import Path
from statsmodels.nonparametric.smoothers_lowess import lowess
from typing import Tuple


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

def prepare_df_for_plot(
    df: pd.DataFrame,
    window_size: int = 9,
    gap_threshold: int = 100
) -> pd.DataFrame:
    """
    Prepare the dataframe for plotting:
    - Remove duplicate frames
    - Sort by frame
    - Break time series over large frame gaps using NaNs
    - Compute rolling moving averages

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe with per-frame statistics
    window_size : int
        Window size for moving average
    gap_threshold : int
        Max allowed frame gap before inserting NaNs
    """

    # --- Drop duplicates & sort ---
    df_event = (
        df.drop_duplicates(subset="frame", keep="first")
          .sort_values(by="frame")
          .reset_index(drop=True)
    )

    # --- Detect frame gaps ---
    frame_diff = df_event["frame"].diff()

    gap_mask = frame_diff > gap_threshold

    # --- Columns affected by gaps (all per-frame stats) ---
    gap_cols = [
        "mean_velocity_per_frame",
        "median_velocity_per_frame",
        "mean_grainsize_per_frame",
        "median_grainsize_per_frame",
        ]

    present_gap_cols = [c for c in gap_cols if c in df_event.columns]

    # --- Insert NaN AFTER a large gap ---
    df_event.loc[gap_mask, present_gap_cols] = np.nan

    # --- Rolling columns mapping ---
    rolling_cols = {
        "mean_velocity_per_frame": "mean_vel_ma",
        "median_velocity_per_frame": "median_vel_ma",
        "mean_grainsize_per_frame": "mean_grain_ma",
        "median_grainsize_per_frame": "median_grain_ma",
        "unique_tracks_per_frame": "tracks_ma",
    }

    # --- Compute moving averages ---
    for col, ma_col in rolling_cols.items():
        if col in df_event.columns:
            df_event[ma_col] = (
                df_event[col]
                .rolling(window=window_size, center=True)
                .mean()
            )

    return df_event


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


def clean_frames_low_detections(df: pd.DataFrame, min_num_detections: int = 1) -> pd.DataFrame:
    """
    Set frame statistics to zero if the number of unique tracks
    is below the minimum threshold.
    """

    cols_to_zero = [
        "mean_vel_ma",
        "mean_grain_ma",
        'mean_velocity_per_frame',
        'mean_grainsize_per_frame'
    ]

    mask = df["unique_tracks_per_frame"] <= min_num_detections

    df.loc[mask, cols_to_zero] = np.nan

    return df

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
        Tracking data. Must contain columns: 'time'

    Returns
    -------
    pd.DataFrame
        Merged DataFrame with interpolated values for both datasets on the common time axis.
    """
    # --- Safety checks ---
    required_piv_cols = ['time_sec', 'vel_un_smoothed', 'vel_smoothed']
    required_mova_cols = ['time']

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
        'frame': interp_series(df_mova.time, df_mova.frame),
        "piv_vel_un_smoothed": interp_series(df_piv.time_sec, df_piv.vel_un_smoothed),
        "piv_vel_smoothed": interp_series(df_piv.time_sec, df_piv.vel_smoothed)
    }

    df_merged = pd.DataFrame(data)

    return df_merged


def compute_track_velocities(
    df_filtered: pd.DataFrame,
    columns: list | None = None,
    lowess_frame_window: int = 20,
    lowess_iterations: int = 0,
) -> Tuple[pd.DataFrame, pd.DataFrame]:

    if columns is None:
        columns = ["frame", "track", "velocity", "grainsize", "time"]


    # 1) Reduce dataframe
    df = df_filtered[columns].copy()

    # Compute one representative frame and summary statistics per track
    # 2) Per-track statistics
    track_velocities = (
        df.groupby("track")
        .agg(
            mean_track_velocity=("velocity", "mean"),
            median_track_velocity=("velocity", "median")
        )
    )

    # 3) Center frame per track
    idx = df.groupby("track").cumcount()
    sizes = df.groupby("track")["frame"].transform("size")
    center_mask = idx == (sizes // 2)

    center_frame = (
        df.loc[center_mask, ["track", "frame"]]
          .set_index("track")["frame"]
          .rename("center_frame")
    )


    # 4) Combine - trackID with center frame + all stats
    # Take all per-track statistics, attach the representative frame of each track,
    # turn the index into a column, and order tracks in time

    df_per_track_velocities = (
        track_velocities
        .join(center_frame)
        .reset_index()
        .sort_values("center_frame")
    )

    # 5) LOWESS smoothing
    n_frames = df["frame"].nunique()
    frac = lowess_frame_window / n_frames

    lowess_mean = lowess(
        endog=df_per_track_velocities["mean_track_velocity"],
        exog=df_per_track_velocities["center_frame"],
        frac=frac,
        it=lowess_iterations,
        return_sorted=True
    )

    lowess_median = lowess(
        endog=df_per_track_velocities["median_track_velocity"],
        exog=df_per_track_velocities["center_frame"],
        frac=frac,
        it=lowess_iterations,
        return_sorted=True
    )

    # Convert LOWESS results into DataFrames (you already did this)
    df_lowess_mean = pd.DataFrame(
        lowess_mean,
        columns=["frame", "lowess_mean_track_velocity"]
    )

    df_lowess_median = pd.DataFrame(
        lowess_median,
        columns=["frame", "lowess_median_track_velocity"]
    )

    # Merge both curves into a single DataFrame, aligned by frame
    df_velocities_lowess = (
        df_lowess_mean
        .merge(df_lowess_median, on="frame", how="outer")
        .drop_duplicates("frame", keep= "first")
        .sort_values("frame")
        .reset_index(drop=True)
    )

    return df_per_track_velocities, df_velocities_lowess


def compute_track_grainsize(
    df_filtered: pd.DataFrame,
    lowess_frame_window: int = 20,
    lowess_iterations: int = 0,
) -> Tuple[pd.DataFrame, pd.DataFrame]:

    if df_filtered.empty:
        raise ValueError(
            "compute_track_grainsize(): df_clean is empty — "
            "cannot compute grain-size statistics."
        )

    cols = ['frame', 'track', 'velocity', 'grainsize', 'bb_width', "bb_center_lidar_x", "bb_center_lidar_y",
            "bb_center_lidar_z", 'time']

    # Reduce size by keeping only essential columns
    df = df_filtered[cols]

    df = df.sort_values(["track", "frame"])

    # Calculate step distance between track appearance
    dxyz = (
        df.groupby("track")[["bb_center_lidar_x", "bb_center_lidar_y", "bb_center_lidar_z"]]
        .diff()
    )

    df["step_distance"] = np.sqrt(
        dxyz["bb_center_lidar_x"] ** 2
        + dxyz["bb_center_lidar_y"] ** 2
        + dxyz["bb_center_lidar_z"] ** 2
    ).fillna(0)

    # Calculate statistic per TRACK
    track_stats = (
        df.groupby("track")
        .agg(
            # grain size
            mean_track_grainsize=("grainsize", "mean"),
            median_track_grainsize=("grainsize", "median"),

            # geometry
            mean_track_bb_width=("bb_width", "mean"),

            # NEW: track length (frames)
            track_length_frames=("frame", "count"),

            # NEW: track duration
            track_duration=("time", lambda x: x.max() - x.min()),

            # NEW: distance traveled
            track_distance=("step_distance", "sum"),
        )
    )

    # 3) Center frame per track
    idx = df.groupby("track").cumcount()
    sizes = df.groupby("track")["frame"].transform("size")
    center_mask = idx == (sizes // 2)

    center_frame = (
        df.loc[center_mask, ["track", "frame"]]
        .set_index("track")["frame"]
        .rename("center_frame")
    )

    # 4) Combine - trackID with center frame + all stats
    # Take all per-track statistics, attach the representative frame of each track,
    # turn the index into a column, and order tracks in time

    df_per_track_grainsize = (
        track_stats
        .join(center_frame)
        .reset_index()
        .sort_values("center_frame")
    )

    # 5) LOWESS smoothing
    n_frames = df["frame"].nunique()
    frac = lowess_frame_window / n_frames

    grainsize_lowess_mean = lowess(
        endog=df_per_track_grainsize["mean_track_grainsize"],
        exog=df_per_track_grainsize["center_frame"],
        frac=frac,
        it=lowess_iterations,
        return_sorted=True
    )

    # Convert LOWESS results into DataFrames (you already did this)
    df_grainsize_lowess = pd.DataFrame(
        grainsize_lowess_mean,
        columns=["frame", "lowess_mean_track_grainsize"]
    )

    return df_per_track_grainsize, df_grainsize_lowess