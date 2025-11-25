from pathlib import Path

from utils.data_filter import filter_tracks_by_movement, filter_rows_upperlimit, filter_tracks_that_jump
from utils.data_utils import load_and_merge_event_data, compute_mean_median_per_frame
from utils.plot_utils import plot_variable_against_frame, prepare_df_for_plot, plot_xy_mov_tracks


def main():

    # Event Details
    event_year = "2024"
    event_month = "06"
    event_day = "14"
    event = f"{event_year}_{event_month}_{event_day}"

    # Output path
    output_dir = Path.cwd() / "output" / event
    output_dir.mkdir(parents=True, exist_ok=True)

    # Choose Frame range to analyse
    start_frame = 0
    end_frame = 100000

    # Load raw Dataframe
    df = load_and_merge_event_data(event)

    #%% FILTER DATA -- Define parameters

    # --- FILTER Data
    # Remove Tracks that jump
    df, df_bad = filter_tracks_that_jump(df, jump_threshold= 5, return_bad=True)
    plot_xy_mov_tracks(df_bad, output_dir=output_dir, title = 'only bad tracks')

    # Remove rows with Outliers (Velocity and Grainsize)
    df = filter_rows_upperlimit(df, velocity_upperlimit = 10, grainsize_upperlimit = 5)

    # Remove Tracks that stay stationary or move less than yaxis_min_length
    df = filter_tracks_by_movement(df, yaxis_min_length=1)
    plot_xy_mov_tracks(df, output_dir=output_dir, title='df filtered')

    #%% Stats PER Frame
    # Compute per-frame statistics
    df_stats = compute_mean_median_per_frame(df)

    # Prepare dataframe for plotting (moving averages)
    df_mova = prepare_df_for_plot(df_stats, window_size=9)


    #%% DATA Visualization - PLOST
    #  --- MEAN Plots
    #  Plot velocity
    plot_variable_against_frame(
        df_mova =df_mova,
        plot_variable="velocity",
        statistic="mean",
        color_ma= "Steelblue",
        label_name= 'velocity',
        y_label= 'Velocity (m/s)',
        y_lim= (0, 10),
        output_dir=output_dir,
        start_frame=start_frame,
        end_frame=end_frame
    )

    # Plot grainsize
    plot_variable_against_frame(
        df_mova =df_mova,
        plot_variable="grainsize",
        statistic="mean",
        color_ma="darkorange",
        label_name='grain size',
        y_label= 'Grain size (m)',
        y_lim=(0, 1),
        output_dir=output_dir,
        start_frame=start_frame,
        end_frame=end_frame
    )

    # Plot tracks
    plot_variable_against_frame(
        df_mova =df_mova,
        plot_variable="tracks",
        statistic="mean",  # statistic is ignored for tracks
        color_ma="red",
        label_name='number of boulder detections',
        y_label='Number of Detections',
        y_lim=(0, df_mova['unique_tracks_per_frame'].max() * 1.1),
        output_dir=output_dir,
        start_frame=start_frame,
        end_frame=end_frame
    )

    # --- Median
    #  Velocity
    plot_variable_against_frame(
        df_mova=df_mova,
        plot_variable="velocity",
        statistic="median",
        color_ma="Steelblue",
        label_name='velocity',
        y_label='Velocity (m/s)',
        y_lim=(0, 10),
        output_dir=output_dir,
        start_frame=start_frame,
        end_frame=end_frame
    )

    # Grainsize
    plot_variable_against_frame(
        df_mova=df_mova,
        plot_variable="grainsize",
        statistic="median",
        color_ma="darkorange",
        label_name='grain size',
        y_label='Grain size (m)',
        y_lim=(0, 1),
        output_dir=output_dir,
        start_frame=start_frame,
        end_frame=end_frame
    )

    print('finished')



if __name__ == "__main__":
    main()

