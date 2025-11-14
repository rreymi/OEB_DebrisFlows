# data_utils.py

import numpy as np
import pandas as pd
from pathlib import Path


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

    # --- Shape ---
    print("\nDataframe shape:", np.shape(df))

    df.info()