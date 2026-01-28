from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


from utils.data_filter import filter_tracks,filter_tracks_by_movement, filter_rows_nonzero_velocity, filter_tracks_that_jump, clean_frames_low_detections
from utils.data_utils import load_and_merge_event_data, compute_mean_median_per_frame, extract_frame_time_table, load_piv_data, merge_piv_and_tracking, compute_track_velocities
from utils.plot_utils import plot_variable_against_frame, prepare_df_for_plot, plot_xy_mov_tracks, \
    plot_piv_and_tracking_velocity, plot_track_velocities_mova_per_frame, plot_track_velocities_mean, \
    plot_track_velocities_lowess


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

    # Load DFS
    df_clean = pd.read_parquet(output_dir / f"df_clean_{event}.parquet")
    df_mova = pd.read_parquet(output_dir / f"df_mova_{event}.parquet")
    df_piv_mova = pd.read_parquet(output_dir / f"df_piv_mova_{event}.parquet")
    df_per_track_statistic = pd.read_parquet(output_dir / f"df_per_track_statistic_{event}.parquet")
    df_lowess = pd.read_parquet(output_dir / f"df_lowess_{event}.parquet")

    # Choose Frame range to analyse------------------------------------------------------------------
    start_frame = 33000
    end_frame = 45000

    #%% Plot parameters
    fig_size = (14,7)

    ylim_velocity = (0, 5)
    ylim_grainsize = (0, 1)

    '''
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
    '''

    #%% Plot X-Y Track Mov --------------------------------------------------------------------------------------
    #plot_xy_mov_tracks(df_bad, title='Bad TrackIDs paths', output_dir=output_dir)

    #plot_xy_mov_tracks(df_clean,title='Filtered TrackIDs paths', output_dir=output_dir)



    #%% Plot PIV and Tracking Velocities ------------------------------------------------------------------------

    plot_piv_and_tracking_velocity(df_piv_mova,df_mova,df_time, event=event, start_frame=start_frame,
                                   end_frame=end_frame, output_dir=output_dir, fig_size=fig_size, ylim_velocity=ylim_velocity)

    '''
    plot_track_velocities_mova_per_frame(df_track_velocities=df_frame_stats,df_mova=df_mova, df_piv_mova=df_piv_mova, event=event, start_frame=start_frame,
                          end_frame=end_frame,df_time=df_time,fig_size=fig_size, output_dir=output_dir, ylim_velocity=ylim_velocity)
    

    plot_track_velocities_mean(df_track_velocities= df_frame_stats,df_piv_mova,
                          event=event, start_frame=start_frame,end_frame=end_frame,
                          df_time=df_time, fig_size=fig_size, output_dir=output_dir,
                          ylim_velocity=ylim_velocity)
    '''
    plot_track_velocities_lowess(df_per_track_statistic, df_lowess, df_piv_mova, stat_type="median",
                          event=event, start_frame=start_frame, end_frame=end_frame,
                          df_time=df_time, fig_size=fig_size, output_dir=output_dir,
                          ylim_velocity=ylim_velocity)



    print('\n === finished :) === \n')

if __name__ == "__main__":
    main()

