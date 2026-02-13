import config
import pandas as pd

from utils.plot_utils import (
    plot_variable_against_frame,
    plot_piv_and_mean_velocity_per_frame,
    plot_track_velocities_lowess,
    plot_track_grainsize_lowess,
    plot_xy_mov_tracks,
    plot_xy_mov_tracks_color_vel,
    plot_track_grainsize_bubble,
    plot_cross_section_velocity,

)

def plot_stats(plot_stats_per_frame, plot_stats_per_track, plot_xy_mov_for_frame_sequence) -> None:

    # --- Load DataFrames
    df_time = pd.read_parquet(config.OUTPUT_DIR/ f"df_time_{config.EVENT}.parquet")
    df_mova = pd.read_parquet(config.OUTPUT_DIR/ f"df_mova_{config.EVENT}.parquet")
    df_piv_mova = pd.read_parquet(config.OUTPUT_DIR/ f"df_piv_mova_{config.EVENT}.parquet")

    if  plot_stats_per_frame:       # Per Frame Plots

        #  --- MEAN Plots
        #  Plot velocity
        plot_variable_against_frame(
            df_mova=df_mova, config= config,
            plot_variable="velocity",
            statistic="mean",
            color_ma="Steelblue",
            label_name='velocity',
            y_label='Velocity (m/s)',
            df_time=df_time,
            y_lim=config.YLIM_VELOCITY,
        )

        # Plot grainsize
        plot_variable_against_frame(
            df_mova=df_mova, config= config,
            plot_variable="grainsize",
            statistic="mean",
            color_ma="darkorange",
            label_name='grain size',
            y_label='Grain Size (m)',
            df_time=df_time,
            y_lim=config.YLIM_VELOCITY,
        )

        # Plot tracks
        plot_variable_against_frame(
            df_mova=df_mova, config= config,
            plot_variable="tracks",
            statistic="mean",  # statistic is ignored for tracks
            color_ma="red",
            label_name='number of detections',
            y_label='Number of Detections',
            y_lim=(0, df_mova['unique_tracks_per_frame'].max() * 1.1),
        )

        # Plot
        plot_piv_and_mean_velocity_per_frame(df_piv_mova, df_mova, df_time, config)




        print("--- Per FRAME plots done --- \n")


    if  plot_stats_per_track:       # ---  Per Track Plots

        # --- Load DataFrames
        df_per_track_velocities = pd.read_parquet(config.OUTPUT_DIR/ f"df_per_track_velocities_{config.EVENT}.parquet")
        df_velocities_lowess = pd.read_parquet(config.OUTPUT_DIR/ f"df_velocities_lowess_{config.EVENT}.parquet")

        # --- Plot Track Velocities
        plot_track_velocities_lowess(df_per_track_velocities, df_velocities_lowess, df_piv_mova, df_time, config)

        print("--- LOWESS Track Velocity plotted --- \n")


    if plot_xy_mov_for_frame_sequence:
        df_clean = pd.read_parquet(config.OUTPUT_DIR/ f"df_clean_{config.EVENT}.parquet")
        df_clean_sequence = df_clean[df_clean['frame'].between(config.START_FRAME,config.END_FRAME)]

        # Track path raw
        plot_xy_mov_tracks(df_clean_sequence, config)

        # Colored by velocity
        plot_xy_mov_tracks_color_vel(df_clean_sequence, config)
        print("--- xy Plot of sequence done --- \n")



def plot_grainsize() -> None:

    # --- Load DataFrames
    df_time = pd.read_parquet(config.OUTPUT_DIR/ f"df_time_{config.EVENT}.parquet")
    df_per_track_grainsize = pd.read_parquet(config.OUTPUT_DIR/ f"df_per_track_grainsize_{config.EVENT}.parquet")
    df_grainsize_lowess = pd.read_parquet(config.OUTPUT_DIR/ f"df_grainsize_lowess_{config.EVENT}.parquet")
    df_per_track_velocities = pd.read_parquet(config.OUTPUT_DIR/ f"df_per_track_velocities_{config.EVENT}.parquet")
    df_velocities_lowess = pd.read_parquet(config.OUTPUT_DIR/ f"df_velocities_lowess_{config.EVENT}.parquet")

    # --- GRAIN SIZE per Track
    plot_track_grainsize_lowess(df_per_track_grainsize, df_grainsize_lowess, df_time, config)
    print("--- Lowess Track Grain size plotted --- \n")

    # --- BUBBLE plot
    plot_track_grainsize_bubble(df_per_track_grainsize, df_per_track_velocities,
                                df_velocities_lowess, df_time, config)
    print("--- Bubble Track Grain size plotted --- \n")




def plot_cross_section() -> None:

    # --- Load DataFrames
    df_clean = pd.read_parquet(config.OUTPUT_DIR/ f"df_clean_{config.EVENT}.parquet")

    plot_cross_section_velocity(df_clean, config)
    print("--- Velocity cross-section plotted --- \n")
