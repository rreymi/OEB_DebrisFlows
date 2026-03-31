# gsd_utils.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

import config
from utils.plot_utils import style_main_axis


def get_grainsizes_in_range(df, start, end):
    return df.loc[
        (df["center_frame"] >= start) &
        (df["center_frame"] <= end),
        "mean_track_grainsize"
    ].dropna()


def compute_gsd_curve(grainsizes):
    gs_sorted = np.sort(grainsizes)
    cdf = np.arange(1, len(gs_sorted) + 1) / len(gs_sorted)
    return gs_sorted, cdf


def get_global_x_limits(gsd_curves):
    min_x = min(curve["x"].min() for curve in gsd_curves)
    max_x = max(curve["x"].max() for curve in gsd_curves)
    return min_x, max_x


# --- GSD per surge and surge type
def plot_gsd_per_surge(
    df_per_track_grainsize,
    df_surges,
    surge_labels,
    surge_colors,
):
    gsd_curves = []

    for _, row in df_surges.iterrows():
        start = row["frame_start"]
        end = row["frame_end"]
        comp = row["components"]

        grainsizes = get_grainsizes_in_range(
            df_per_track_grainsize, start, end
        )

        if len(grainsizes) == 0:
            continue

        x, y = compute_gsd_curve(grainsizes)

        gsd_curves.append({
            "x": x,
            "y": y,
            "components": comp
        })

    fig, ax = plt.subplots(figsize=(8, 8))

    seen = set()

    for curve in gsd_curves:
        label_name = surge_labels.get(curve["components"], "Unknown")
        color = surge_colors.get(label_name, "black")

        label = label_name if label_name not in seen else None
        seen.add(label_name)

        ax.plot(
            curve["x"], curve["y"],
            color=color,
            alpha=0.8,
            linewidth=2,
            label=label)

    # limits
    min_x, max_x = get_global_x_limits(gsd_curves)

    style_main_axis(
        ax=ax,
        xlabel="Grain Size (m)",
        ylabel="GSD",
        ylim=(0,1),
        xlim= (0,1.5),
        add_grid=True,
    )

    ax.legend(
        title=f"Event {config.EVENT}\n\n"
              "Component Classes",
        title_fontsize=12,
        edgecolor="black",
        facecolor="white",
        framealpha=0.8,
        frameon=True,
        fontsize=12,
    )

    # --- Save
    fig_name = f'GSD_per_surge_type_{config.EVENT}'
    output_dir_for_plots = Path(config.OUTPUT_DIR)
    output_path = Path(output_dir_for_plots) / fig_name
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

# --- GSD complete Event
def plot_gsd_single_event(
    df_per_track_grainsize,
    event_name=None,
):
    grainsizes = get_grainsizes_in_range(
        df_per_track_grainsize,
        df_per_track_grainsize["center_frame"].min(),
        df_per_track_grainsize["center_frame"].max(),
    )

    x, y = compute_gsd_curve(grainsizes)

    fig, ax = plt.subplots(figsize=(8, 8))

    ax.plot(
        x, y,
        alpha=0.8,
        linewidth=2,
        label=event_name)


    style_main_axis(
        ax=ax,
        xlabel="Grain Size (m)",
        ylabel="GSD",
        ylim=(0, 1),
        xlim=(0, 1.5),
        add_grid=True,
    )

    ax.legend(
        title="Event",
        title_fontsize=12,
        edgecolor="black",
        facecolor="white",
        framealpha=0.8,
        frameon=True,
        fontsize=12,
    )

    # --- Save
    fig_name = f'GSD_complete_event_{config.EVENT}'
    output_dir_for_plots = Path(config.OUTPUT_DIR)
    output_path = Path(output_dir_for_plots) / fig_name
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_gsd_all_events(
    events,
    base_output_dir=Path.cwd() / "output",
):
    gsd_curves = []

    for event in events:
        output_dir = base_output_dir / event

        df = pd.read_parquet(
            output_dir / f"df_per_track_grainsize_{event}.parquet"
        )

        grainsizes = get_grainsizes_in_range(
            df,
            df["center_frame"].min(),
            df["center_frame"].max(),
        )

        if len(grainsizes) == 0:
            continue

        x, y = compute_gsd_curve(grainsizes)

        gsd_curves.append({
            "event": event,
            "x": x,
            "y": y
        })

    fig, ax = plt.subplots(figsize=(8, 8))

    for curve in gsd_curves:
        ax.plot(curve["x"], curve["y"],
                alpha=0.8,
                linewidth=2,
                label=curve["event"])

    # limits
    min_x, max_x = get_global_x_limits(gsd_curves)

    style_main_axis(
        ax=ax,
        xlabel="Grain Size (m)",
        ylabel="GSD",
        ylim=(0, 1),
        xlim=(0, max_x),
        add_grid=True,
    )

    ax.legend(
        title="Events",
        title_fontsize=12,
        edgecolor="black",
        facecolor="white",
        framealpha=0.8,
        frameon=True,
        fontsize=12,
    )
    # --- Save
    fig_name = f'GSD_all_events_{config.EVENT}'
    output_dir_for_plots = Path(config.OUTPUT_DIR)
    output_path = Path(output_dir_for_plots) / fig_name
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)