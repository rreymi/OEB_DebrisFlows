import config

from utils.data_filter import (
    filter_tracks,
    filter_tracks_by_movement,
    filter_tracks_that_jump,
    replace_zero_velocity_with_nan
)

from utils.data_utils import load_and_merge_event_data, extract_frame_time_table

def filter_process():

    # --- Event ---
    event = config.EVENT

    # --- Load raw Data ---
    df_raw = load_and_merge_event_data(event)

    # --- Extract df_time for later
    df_time = extract_frame_time_table(df_raw)

    # --- Apply filters ---
    # Step 1
    df_filtered_01 = filter_tracks(
        df_raw,
        min_track_length=config.MIN_TRACK_LENGTH,
        max_track_length=config.MAX_TRACK_LENGTH,
        max_std_track_vel=config.MAX_STD_TRACK_VEL,
        min_median_track_vel=config.MIN_MEDIAN_TRACK_VEL,
    )
    # Step 2
    df_filtered_02, df_bad = filter_tracks_that_jump(
        df_filtered_01,
        jump_threshold=config.JUMP_THRESHOLD,
        return_bad_df=True,
    )
    # Step 3
    df_filtered_03, df_yaxis_movement = filter_tracks_by_movement(
        df_filtered_02,
        yaxis_min_length=config.YAXIS_MIN_LENGTH,
    )
    # Step 4
    df_clean = replace_zero_velocity_with_nan(df_filtered_03)

    # df_clean = df_raw

    # --- Summary ---
    n_tracks = df_clean["track"].nunique()
    n_tracks_raw = df_raw["track"].nunique()
    print(
        f"\nFiltering summary:\n"
        f"Total track IDs in DF:     {n_tracks_raw}\n"
        f"Removed track IDs:   {n_tracks_raw - n_tracks}\n"
        f"Remaining track IDs: {n_tracks}\n"
        
        f"\n"
        f"First Image Frame:   {df_clean['frame'].min()}\n"
        f"Last Image Frame:   {df_clean['frame'].max()}\n"
        f"Total number of Image Frames:   {df_clean['frame'].nunique()}\n"
    )

    # --- Save DFs---
    df_clean.to_parquet(config.OUTPUT_DIR / f"df_clean_{event}.parquet")
    df_time.to_parquet(config.OUTPUT_DIR / f"df_time_{event}.parquet")
    df_bad.to_parquet(config.OUTPUT_DIR / f"df_bad_{event}.parquet")
    df_yaxis_movement.to_parquet(config.OUTPUT_DIR / f"yaxis_movement_{event}.parquet")

    print("\n--- Filter process finished ---")
    print("df_clean and df_time saved")
