from pathlib import Path

from utils.data_filter import filter_tracks_by_movement, filter_rows_upperlimit, compute_mean_median_per_frame
from utils.data_utils import load_and_merge_event_data
from utils.plot_utils import plot_variable_against_frame, prepare_df_for_plot


def main():

    # Event
    event_year = "2024"
    event_month = "06"
    event_day = "14"
    event = f"{event_year}_{event_month}_{event_day}"

    # Output path
    output_dir = Path.cwd() / "output" / event
    output_dir.mkdir(parents=True, exist_ok=True)

    # Choose Frame range to analyse
    start_frame = 30000
    end_frame = 41000

    # Load raw Dataframe
    df = load_and_merge_event_data(event)


    # --- FILTER Data
    df = filter_rows_upperlimit(df, velocity_upperlimit = 15, grainsize_upperlimit = 5)
    #df = filter_tracks_by_movement(df, yaxis_min_length=2.0)

    # Compute per-frame statistics
    df_stats = compute_mean_median_per_frame(df)

    # Prepare dataframe for plotting (moving averages)
    df_mova = prepare_df_for_plot(df_stats, window_size=9)

    #  --- MEAN Plots
    #  Plot velocity
    plot_variable_against_frame(
        df_mova =df_mova,
        plot_variable="velocity",
        statistic="mean",
        color_ma= "Steelblue",
        label_name= 'Velocity',
        y_label= 'Velocity (m/s)',
        y_lim= (0, 12),
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
        label_name='Grain size',
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
        label_name='Number of boulder detections',
        y_label='Number of Detections',
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
        label_name='Velocity',
        y_label='Velocity (m/s)',
        y_lim=(0, 12),
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
        label_name='Grain size',
        y_label='Grain size (m)',
        y_lim=(0, 1),
        output_dir=output_dir,
        start_frame=start_frame,
        end_frame=end_frame
    )





if __name__ == "__main__":
    main()

