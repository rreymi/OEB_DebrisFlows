from pathlib import Path

from utils.data_filter import filter_tracks,filter_tracks_by_movement, filter_rows_nonzero_velocity, filter_tracks_that_jump, clean_frames_low_detections
from utils.data_utils import load_and_merge_event_data, compute_mean_median_per_frame, extract_frame_time_table, load_piv_data, merge_piv_and_tracking
from utils.plot_utils import plot_variable_against_frame, prepare_df_for_plot, plot_xy_mov_tracks, plot_piv_and_tracking_velocity


def main():

    # Event Details
    event_year = "2024"
    event_month = "06"
    event_day = "14"

    event = f"{event_year}_{event_month}_{event_day}"

    # Output path
    output_dir = Path.cwd() / "output" / event
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load raw Dataframe
    df_raw = load_and_merge_event_data(event)

    # create time dataframe for plotting
    df_time = extract_frame_time_table(df_raw)


    #%% FILTER DATA -- Define parameters ----------------------------------------------------------------------------

    # Choose Frame range to analyse
    start_frame = 32000
    end_frame = 46000

    # Define track lengths
    min_track_length = 5
    max_track_length = 300

    # Velocity limits
    max_std_track_vel = 1
    min_median_track_vel = 0.1

    # Jumping threshold
    jump_threshold = 1

    # Y-axis movement
    yaxis_min_length = 0.5

    #%% Plot parameters

    fig_size = (14,7)

    # Moving Average, parameters
    window_size = 7
    gap_threshold = 400

    ylim_velocity = (0, 5)
    ylim_grainsize = (0, 1)

    #%%-- FILTER DATA -- apply filter functions ---------------------------------------------------------------------





    #df_clean = df_raw
    n_tracks = df_clean['track'].nunique()
    n_tracks_raw = df_raw['track'].nunique()
    print(f"\nFiltering summary:\n"
        f"  Remaining track IDs: {n_tracks}\n"
        f"  Removed track IDS:   {n_tracks_raw - n_tracks}\n"
        f"  Total tracks IDs:    {n_tracks_raw}")



    #%% Stats PER Frame --------------------------------------------------------------------------------------





    print('\n === finished :) === \n')

if __name__ == "__main__":
    main()

