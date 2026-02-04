import pandas as pd

from utils.data_utils import compute_track_grainsize

import config

def calculate_gsd() -> None:

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

    return

