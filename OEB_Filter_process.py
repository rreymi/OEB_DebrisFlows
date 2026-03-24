import config
import logging

from utils.data_filter import (
    filter_tracks_range,
    rolling_median_filter,
    filter_tracks_by_movement,
    filter_tracks_that_jump,
    filter_tracks_by_stats
)

from utils.data_utils import load_and_merge_event_data, extract_frame_time_table

def filter_process():
    logging.info("Filter Process started...")

    # --- Load raw Data ---
    df_raw = load_and_merge_event_data(config.EVENT)

    # --- Extract df_time for later
    df_time = extract_frame_time_table(df_raw)

    # --- Apply filters ---
    # Step 1 - Remove clear OUTLIERS and replace zeros with NANS
    df_filtered_01 = filter_tracks_range(
        df_raw,
        vel_range=config.VELOCITY_RANGE,
        gs_range=config.GRAINSIZE_RANGE,
    )

    # Step 2 - Rolling MEDIAN Filter to remove spikes/artifacts in DATA
    df_filtered_02 = rolling_median_filter(
        df_filtered_01,
        min_window=config.MIN_ROLL_WINDOW,
        max_window=config.MAX_ROLL_WINDOW)

    # Step 3 - FILTER out TrackIDS that have a small Y-AXIS movement
    df_filtered_03 = filter_tracks_by_movement(
        df_filtered_02,
        yaxis_min_length=config.YAXIS_MIN_LENGTH)

    # Step 4 - Filter out tracks that jump
    df_filtered_04, df_bad = filter_tracks_that_jump(
        df_filtered_03,
        jump_threshold=config.JUMP_THRESHOLD,
    )

    # Step 5 - Filter out track that move very slow
    df_clean = filter_tracks_by_stats(
        df_filtered_04,
        min_median_track_vel=config.MIN_MEDIAN_TRACK_VEL,
    )

    # --- Summary ---
    n_tracks = df_clean["track"].nunique()
    n_tracks_raw = df_raw["track"].nunique()

    logging.info(f" --- Filtering summary:\n"
        f"Total track IDs in DF:     {n_tracks_raw}\n"
        f"Removed track IDs:   {n_tracks_raw - n_tracks}\n"
        f"Remaining track IDs: {n_tracks}\n"
        
        f"\n"
        f"First Image Frame:   {df_clean['frame'].min()}\n"
        f"Last Image Frame:   {df_clean['frame'].max()}\n"
        f"Total number of Image Frames:   {df_clean['frame'].nunique()}\n"
        "\n--- Filter process finished ---\n"
    )

    # --- Save DFs---
    df_raw.to_parquet(config.OUTPUT_DIR / f"df_raw_{config.EVENT}.parquet")
    df_clean.to_parquet(config.OUTPUT_DIR / f"df_clean_{config.EVENT}.parquet")
    df_time.to_parquet(config.OUTPUT_DIR / f"df_time_{config.EVENT}.parquet")
    df_bad.to_parquet(config.OUTPUT_DIR / f"df_bad_{config.EVENT}.parquet")
