import config
import pandas as pd


from utils.data_utils import (
    compute_mean_median_per_frame,
    compute_track_velocities,
    prepare_df_for_plot,
    load_piv_data,
    merge_piv_and_tracking,
    clean_frames_low_detections,
    compute_track_grainsize
)

def calculate_vel(run_calc_per_frame = True, run_calc_per_track = True)-> None:

    event = config.EVENT
    output_dir = config.OUTPUT_DIR

    # -------------------------------------------------------------------------
    # Load Clean DataFrame
    # -------------------------------------------------------------------------
    df_clean = pd.read_parquet(output_dir / f"df_clean_{event}.parquet")

    if run_calc_per_frame:
        # -------------------------------------------------------------------------
        # Compute Statistics Per Frame
        # -------------------------------------------------------------------------
        # Compute per-frame mean and median statistics
        df_stats = compute_mean_median_per_frame(df_clean)

        # Save per-frame statistics as CSV
        df_stats.to_csv(output_dir / f"df_stats_{event}.csv", index=False)

        # Prepare moving-average DataFrame for plotting
        df_mova = prepare_df_for_plot(
            df_stats,
            window_size=config.MOVING_AVERAGE_WINDOW_SIZE,
            gap_threshold=config.GAP_THRESHOLD
        )

        # Remove frames with very few detections
        df_mova = clean_frames_low_detections(
            df_mova,
            min_num_detections=config.MIN_NUM_DETECTIONS
        )

        # Save moving-average CSV
        df_mova.to_csv(output_dir / f"df_mova_{event}.csv", index=False)
        df_mova.to_parquet(output_dir / f"df_mova_{event}.parquet")

        # Load and Save PIV Velocities
        df_piv = load_piv_data(event=event)
        df_piv_mova = merge_piv_and_tracking(df_piv, df_mova)
        df_piv_mova.to_parquet(output_dir / f"df_piv_mova_{event}.parquet")
        print(f"\nStatistics calculation per FRAME complete for event {event}.")


    if run_calc_per_track:
        # -------------------------------------------------------------------------
        # Compute Statistics Per Track
        # -------------------------------------------------------------------------
        df_per_track_velocities, df_velocities_lowess = compute_track_velocities(
            df_clean,
            lowess_frame_window=config.LOWESS_FRAME_WINDOW_SIZE,
            lowess_iterations=config.LOWESS_ITERATIONS,
            lowess_gap_threshold=config.LOWESS_GAP_THRESHOLD,
            lowess_segment_length=config.LOWESS_SEGMENT_LENGTH
        )

        # Save track-based statistics
        df_per_track_velocities.to_parquet(
            output_dir / f"df_per_track_velocities_{event}.parquet"
        )
        df_velocities_lowess.to_parquet(
            output_dir / f"df_velocities_lowess_{event}.parquet"
        )
        print(f"\nStatistics calculation per TRACK complete for event {event}.")



def calculate_gs() -> None:

    event = config.EVENT
    output_dir = config.OUTPUT_DIR

    # -------------------------------------------------------------------------
    # Load Clean DataFrame
    # -------------------------------------------------------------------------
    df_clean = pd.read_parquet(output_dir / f"df_clean_{event}.parquet")

    df_per_track_grainsize, df_grainsize_lowess = compute_track_grainsize(
            df_clean,
            lowess_frame_window=config.LOWESS_FRAME_WINDOW_SIZE,
            lowess_iterations=config.LOWESS_ITERATIONS
    )

    # Save track-based statistics
    df_per_track_grainsize.to_parquet(
        output_dir / f"df_per_track_grainsize_{event}.parquet"
    )
    df_grainsize_lowess.to_parquet(
        output_dir / f"df_grainsize_lowess_{event}.parquet"
    )
    print(f"\nGrain Size calculation per TRACK complete for event {event}.")


