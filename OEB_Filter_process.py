import config

from utils.data_filter import (
    filter_tracks,
    filter_tracks_by_movement,
    filter_tracks_that_jump,
    replace_zero_velocity_with_nan
)

from utils.plot_utils import plot_xy_mov_tracks
from utils.data_utils import load_and_merge_event_data, extract_frame_time_table

def filter_process(plot_xy_movement: bool = True):

    # --- Event ---
    event = config.EVENT


    # --- Output path ---
    output_dir = config.OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)


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
        return_bad=True,
    )
    # Step 3
    df_filtered_03, df_yaxis_movement = filter_tracks_by_movement(
        df_filtered_02,
        yaxis_min_length=config.YAXIS_MIN_LENGTH,
    )
    # Step 4
    df_clean = replace_zero_velocity_with_nan(df_filtered_03)

    # --- Summary ---
    n_tracks = df_clean["track"].nunique()
    n_tracks_raw = df_raw["track"].nunique()
    print(
        f"\nFiltering summary:\n"
        f"  Remaining track IDs: {n_tracks}\n"
        f"  Removed track IDs:   {n_tracks_raw - n_tracks}\n"
        f"  Total track IDs:     {n_tracks_raw}"
    )

    # --- Save DFs---
    df_clean.to_parquet(output_dir / f"df_clean_{event}.parquet")
    df_time.to_parquet(output_dir / f"df_time_{event}.parquet")

    df_yaxis_movement.to_parquet(output_dir / f"yaxis_movement_{event}.parquet")

    print("\n--- Filter process finished ---")
    print("df_clean and df_time saved")


    # --- Plot track path on x and y plane (All tracks / Bad Tracks and good Tracks of frame sequence)
    if plot_xy_movement:

        print("plotting xy movements...")
        plot_xy_mov_tracks(df_bad, title='Bad TrackIDs paths - complete Event', output_dir=output_dir)

        plot_xy_mov_tracks(df_clean,title='Filtered TrackIDs paths - complete Event', output_dir=output_dir)

        print("done")
