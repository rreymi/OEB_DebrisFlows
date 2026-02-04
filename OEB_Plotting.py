import config
import pandas as pd

from utils.plot_utils import (
    plot_variable_against_frame,
    plot_piv_and_mean_velocity_per_frame,
    plot_track_velocities_lowess,
    plot_track_grainsize_lowess,
    plot_xy_mov_tracks,
)

def plot_stats(plot_stats_per_frame, plot_stats_per_track, plot_xy_mov_for_frame_sequence) -> None:

    # Config Details
    event = config.EVENT
    start_frame = config.START_FRAME
    end_frame = config.END_FRANE
    output_dir = config.OUTPUT_DIR
    fig_size = config.FIG_SIZE
    ylim_velocity = config.YLIM_VELOCITY
    ylim_grainsize = config.YLIM_GRAINSIZE


    # -------------------------------------------------------------------------
    # Load DataFrames - general
    # -------------------------------------------------------------------------
    df_time = pd.read_parquet(output_dir / f"df_time_{event}.parquet")
    df_mova = pd.read_parquet(output_dir / f"df_mova_{event}.parquet")
    df_piv_mova = pd.read_parquet(output_dir / f"df_piv_mova_{event}.parquet")



    if  plot_stats_per_frame:
        # -------------------------------------------------------------------------
        # Per Frame Plots
        # -------------------------------------------------------------------------

        #  --- MEAN Plots
        #  Plot velocity
        plot_variable_against_frame(
            df_mova=df_mova,
            plot_variable="velocity",
            statistic="mean",
            color_ma="Steelblue",
            label_name='velocity',
            y_label='Velocity (m/s)',
            y_lim=ylim_velocity, output_dir=output_dir, start_frame=start_frame, end_frame=end_frame, df_time=df_time,
            fig_size=fig_size)

        # Plot grainsize
        plot_variable_against_frame(
            df_mova=df_mova,
            plot_variable="grainsize",
            statistic="mean",
            color_ma="darkorange",
            label_name='grain size',
            y_label='Grain Size (m)',
            y_lim=ylim_grainsize, output_dir=output_dir, start_frame=start_frame, end_frame=end_frame, df_time=df_time,
            fig_size=fig_size)

        # Plot tracks
        plot_variable_against_frame(
            df_mova=df_mova,
            plot_variable="tracks",
            statistic="mean",  # statistic is ignored for tracks
            color_ma="red",
            label_name='number of detections',
            y_label='Number of Detections',
            y_lim=(0, df_mova['unique_tracks_per_frame'].max() * 1.1),
            output_dir=output_dir, start_frame=start_frame, end_frame=end_frame, df_time=df_time, fig_size=fig_size)

        # Plot number of lost tracks
        # todo?


        # Plot
        plot_piv_and_mean_velocity_per_frame(df_piv_mova, df_mova, df_time, event=event, start_frame=start_frame,
                                       end_frame=end_frame, output_dir=output_dir, fig_size=fig_size,
                                       ylim_velocity=ylim_velocity)




        print("--- Per FRAME plots done --- \n")

    if  plot_stats_per_track:
        # -------------------------------------------------------------------------
        # Per Track Plots
        # -------------------------------------------------------------------------

        # Load DFs
        df_per_track_velocities = pd.read_parquet(output_dir / f"df_per_track_velocities_{event}.parquet")
        df_velocities_lowess = pd.read_parquet(output_dir / f"df_velocities_lowess_{event}.parquet")

        plot_track_velocities_lowess(df_per_track_velocities, df_velocities_lowess, df_piv_mova, stat_type=config.STATISTIC_TYPE,
                                     event=event, start_frame=start_frame, end_frame=end_frame,
                                     df_time=df_time, fig_size=fig_size, output_dir=output_dir,
                                     ylim_velocity=ylim_velocity)
        print("--- Per TRACK plots done --- \n")


    if plot_xy_mov_for_frame_sequence:
        df_clean = pd.read_parquet(output_dir / f"df_clean_{event}.parquet")
        df_clean_sequence = df_clean[df_clean['frame'].between(start_frame,end_frame)]

        plot_xy_mov_tracks(df_clean_sequence, title=f'xy_track_path_mov_{event}_{start_frame}_{end_frame}',
                           output_dir=output_dir)
        print("--- xy Plot of sequence done --- \n")



def plot_grainsize(df_per_track_grainsize: pd.DataFrame,
             df_grainsize_lowess: pd.DataFrame,
             ) -> None:

    # Config Details
    event = config.EVENT
    start_frame = config.START_FRAME
    end_frame = config.END_FRANE
    output_dir = config.OUTPUT_DIR
    fig_size = config.FIG_SIZE
    ylim_grainsize = config.YLIM_GRAINSIZE

    # -------------------------------------------------------------------------
    # Load DataFrames - general
    # -------------------------------------------------------------------------
    df_time = pd.read_parquet(output_dir / f"df_time_{event}.parquet")
    df_piv_mova = pd.read_parquet(output_dir / f"df_piv_mova_{event}.parquet")

    plot_track_grainsize_lowess(df_per_track_grainsize, df_grainsize_lowess, df_piv_mova,
                                event=event, start_frame=start_frame, end_frame=end_frame,
                                df_time=df_time, fig_size=fig_size, output_dir=output_dir,
                                ylim_grainsize=ylim_grainsize)

