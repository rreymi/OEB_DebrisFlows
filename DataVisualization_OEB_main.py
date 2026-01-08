from pathlib import Path

from utils.data_filter import filter_tracks,filter_tracks_by_movement, filter_rows_nonzero_velocity, filter_tracks_that_jump, clean_frames_low_detections
from utils.data_utils import load_and_merge_event_data, compute_mean_median_per_frame, extract_frame_time_table, load_piv_data, merge_piv_and_tracking, compute_track_velocities
from utils.plot_utils import plot_variable_against_frame, prepare_df_for_plot, plot_xy_mov_tracks, plot_piv_and_tracking_velocity, plot_track_velocities


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
    start_frame = 9500
    end_frame = 13000

    # Define track lengths
    min_track_length = 5
    max_track_length = 300

    # Velocity limits
    max_std_track_vel = 1.5
    min_median_track_vel = 0.1

    # Jumping threshold
    jump_threshold = 1

    # Y-axis movement
    yaxis_min_length = 0.4

    #%% Plot parameters

    fig_size = (14,7)

    # Moving Average, parameters
    window_size = 7
    gap_threshold = 400

    ylim_velocity = (0, 5)
    ylim_grainsize = (0, 1)

    #%%-- FILTER DATA -- apply filter functions ---------------------------------------------------------------------

    # --- Filter TRACKS
    df_filtered_01 = filter_tracks(df_raw, min_track_length=min_track_length, max_track_length=max_track_length,
                                      max_std_track_vel=max_std_track_vel, min_median_track_vel=min_median_track_vel)


    # --- Remove Tracks that jump
    df_filtered_02, df_bad = filter_tracks_that_jump(df_filtered_01, jump_threshold= jump_threshold,return_bad=True)


    # --- Remove Tracks that stay stationary or move less than yaxis_min_length
    df_filtered_03 = filter_tracks_by_movement(df_filtered_02, yaxis_min_length=yaxis_min_length)

    # Only keep nonzero Velocity-rows
    df_filtered_04 = filter_rows_nonzero_velocity(df_filtered_03)



    df_clean = df_filtered_04
    #df_clean = df_raw
    n_tracks = df_clean['track'].nunique()
    n_tracks_raw = df_raw['track'].nunique()
    print(f"\nFiltering summary:\n"
        f"  Remaining track IDs: {n_tracks}\n"
        f"  Removed track IDS:   {n_tracks_raw - n_tracks}\n"
        f"  Total tracks IDs:    {n_tracks_raw}")



    #%% Stats PER Frame --------------------------------------------------------------------------------------
    # Compute per-frame statistics and keep only essential cols
    df_stats = compute_mean_median_per_frame(df_clean)

    # save CSV of STATS after Filtering
    #df_stats.to_csv(output_dir / f"df_stats_{event}.csv")

    # Prepare dataframe for plotting (moving averages)
    df_mova = prepare_df_for_plot(df_stats, window_size=window_size, gap_threshold=gap_threshold)

    # clean frames with very low number of detections
    df_mova = clean_frames_low_detections(df_mova, min_num_detections = 2)

    # save CSV of MOVA (plot table)
    #df_mova.to_csv(output_dir / f"df_mova_{event}.csv")


    #%% Stats PER Track --------------------------







    #%% DATA Visualization - PLOTS --------------------------------------------------------------------------------
    #  --- MEAN Plots
    #  Plot velocity
    plot_variable_against_frame(
        df_mova =df_mova,
        plot_variable="velocity",
        statistic="mean",
        color_ma= "Steelblue",
        label_name= 'velocity',
        y_label= 'Velocity (m/s)',
        y_lim= ylim_velocity,output_dir=output_dir,start_frame=start_frame,end_frame=end_frame,df_time = df_time,fig_size= fig_size)

    # Plot grainsize
    plot_variable_against_frame(
        df_mova =df_mova,
        plot_variable="grainsize",
        statistic="mean",
        color_ma="darkorange",
        label_name='grain size',
        y_label= 'Grain size (m)',
        y_lim=ylim_grainsize, output_dir=output_dir, start_frame=start_frame, end_frame=end_frame, df_time=df_time,fig_size=fig_size)

    # Plot tracks
    plot_variable_against_frame(
        df_mova =df_mova,
        plot_variable="tracks",
        statistic="mean",  # statistic is ignored for tracks
        color_ma="red",
        label_name='number of boulder detections',
        y_label='Number of Detections',
        y_lim=(0, df_mova['unique_tracks_per_frame'].max() * 1.1),
        output_dir=output_dir,start_frame=start_frame,end_frame=end_frame,df_time=df_time,fig_size=fig_size)



    # Plot number of lost tracks
    plot_variable_against_frame(
        df_mova=df_mova,
        plot_variable="tracks",
        statistic="mean",  # statistic is ignored for tracks
        color_ma="red",
        label_name='number of boulder detections',
        y_label='Number of Detections',
        y_lim=(0, df_mova['unique_tracks_per_frame'].max() * 1.1),
        output_dir=output_dir, start_frame=start_frame, end_frame=end_frame, df_time=df_time, fig_size=fig_size)




    #%% Plot X-Y Track Mov --------------------------------------------------------------------------------------
    #plot_xy_mov_tracks(df_bad, title='Bad TrackIDs paths', output_dir=output_dir)

    #plot_xy_mov_tracks(df_clean,title='Filtered TrackIDs paths', output_dir=output_dir)



    #%% Plot PIV and Tracking Velocities ------------------------------------------------------------------------

    df_piv = load_piv_data(event=event)
    df_piv_mova = merge_piv_and_tracking(df_piv, df_mova)

    plot_piv_and_tracking_velocity(df_piv_mova, event=event, start_frame=start_frame,
                                   end_frame=end_frame, output_dir=output_dir, fig_size=fig_size)


    df_track_velocities = compute_track_velocities(df_clean)

    plot_track_velocities(df_track_velocities=df_track_velocities,df_mova=df_mova, df_piv_mova=df_piv_mova, event=event, start_frame=start_frame,
                          end_frame=end_frame,df_time=df_time,fig_size=fig_size, output_dir=output_dir)



    print('\n === finished :) === \n')

if __name__ == "__main__":
    main()

