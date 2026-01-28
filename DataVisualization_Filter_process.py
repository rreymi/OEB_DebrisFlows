import config

from utils.data_filter import (
    filter_tracks,
    filter_tracks_by_movement,
    filter_rows_nonzero_velocity,
    filter_tracks_that_jump,
)

from utils.data_utils import load_and_merge_event_data, extract_frame_time_table

def filter_process():

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
    df_filtered_01 = filter_tracks(
        df_raw,
        min_track_length=config.MIN_TRACK_LENGTH,
        max_track_length=config.MAX_TRACK_LENGTH,
        max_std_track_vel=config.MAX_STD_TRACK_VEL,
        min_median_track_vel=config.MIN_MEDIAN_TRACK_VEL,
    )

    df_filtered_02, df_bad = filter_tracks_that_jump(
        df_filtered_01,
        jump_threshold=config.JUMP_THRESHOLD,
        return_bad=True,
    )

    df_filtered_03 = filter_tracks_by_movement(
        df_filtered_02,
        yaxis_min_length=config.YAXIS_MIN_LENGTH,
    )

    df_clean = filter_rows_nonzero_velocity(df_filtered_03)

    # --- Summary ---
    n_tracks = df_clean["track"].nunique()
    n_tracks_raw = df_raw["track"].nunique()

    print(
        f"\nFiltering summary:\n"
        f"  Remaining track IDs: {n_tracks}\n"
        f"  Removed track IDs:   {n_tracks_raw - n_tracks}\n"
        f"  Total track IDs:     {n_tracks_raw}"
    )

    # --- Save ---
    df_clean.to_parquet(output_dir / f"df_clean_{event}.parquet")
    df_time.to_parquet(output_dir / f"df_time_{event}.parquet")

    print("\n--- Filter process finished ---")
    print("df_clean and df_time saved")


if __name__ == "__main__":
    filter_process()