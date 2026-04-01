import config
import pandas as pd

from utils.gsd_utils import (
    plot_gsd_per_surge,
    plot_gsd_single_event,
    plot_gsd_all_events,
    plot_surge_types_comparison
)


def plot_gsd(plot_gsd_all: bool) -> None:

    # --- Mapping ---
    surge_labels = {
        1: "Granular",
        2: "Low viscosity",
        3: "Mushy",
        4: "Not classified"
    }

    surge_colors = {
        "Granular": "sandybrown",
        "Low viscosity": "skyblue",
        "Mushy": "yellowgreen",
        "Not classified": "lightgray"
    }

    df_per_track_grainsize = pd.read_parquet(config.OUTPUT_DIR/ f"df_per_track_grainsize_{config.EVENT}.parquet")

    df_surges = pd.read_csv(
        f"input_data/{config.EVENT}/surge_classification_{config.EVENT}.csv",
        sep=";"
    )

    df_gsd_stats = plot_gsd_per_surge(
        df_per_track_grainsize= df_per_track_grainsize,
        df_surges = df_surges,
        surge_labels= surge_labels,
        surge_colors= surge_colors)

    # plot_gsd_single_event(
    #     df_per_track_grainsize=df_per_track_grainsize,
    #     event_name=config.EVENT,
    # )


    plot_surge_types_comparison(df_gsd_stats, surge_labels, surge_colors)



    if plot_gsd_all:

        events = [
            "2024_06_14",
            "2024_06_15c",
            "2024_06_21c",
            "2024_06_25",
            "2024_07_01a",
            "2024_07_01b",
        ]
        plot_gsd_all_events(events)
        pass


