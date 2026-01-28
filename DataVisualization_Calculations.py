import pandas as pd

import config

from utils.data_filter import (
    clean_frames_low_detections
)

from utils.data_utils import (
    compute_mean_median_per_frame, compute_track_velocities
)

from utils.plot_utils import (
    prepare_df_for_plot
)


def calculate_stats(run_calc_per_frame = True, run_calc_per_track = True):

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

        print(f"\nStatistics calculation per FRAME complete for event {event}.")


    if run_calc_per_track:
        # -------------------------------------------------------------------------
        # Compute Statistics Per Track
        # -------------------------------------------------------------------------
        df_per_track_statistic, df_lowess = compute_track_velocities(
            df_clean,
            lowess_frame_window=config.LOWESS_FRAME_WINDOW_SIZE,
            lowess_iterations=config.LOWESS_ITERATIONS
        )

        # Save track-based statistics
        df_per_track_statistic.to_parquet(
            output_dir / f"df_per_track_statistic_{event}.parquet"
        )
        df_lowess.to_parquet(
            output_dir / f"df_lowess_{event}.parquet"
        )
        print(f"\nStatistics calculation per TRACK complete for event {event}.")



if __name__ == "__main__":
    calculate_stats()