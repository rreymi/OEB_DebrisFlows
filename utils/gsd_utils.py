# gsd_utils.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from sympy.printing.pretty.pretty_symbology import line_width

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

        n_tracks = len(grainsizes)
        if n_tracks == 0:
            continue

        x, y = compute_gsd_curve(grainsizes)

        gsd_curves.append({
            "x": x,
            "y": y,
            "components": comp,
            'start_frame': start,
            'end_frame': end,
            'number of tracks': n_tracks,
            'track rate': n_tracks / (end - start),
            'd50': np.percentile(grainsizes, 50),
            'd95': np.percentile(grainsizes, 95),
        })

    df_stats = pd.DataFrame(gsd_curves)

    # keep only what you want
    df_stats = df_stats[
        [
            "start_frame",
            "end_frame",
            "components",
            "number of tracks",
            'track rate',
            "d50",
            "d95",
        ]
    ]

    out_path = config.OUTPUT_DIR / f"gsd_stats_{config.EVENT}.csv"
    df_stats.to_csv(out_path, index=False)

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

    return df_stats

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



# Compare Debris flow surges
def plot_surge_types_comparison(df_gsd_stats, surge_labels, surge_colors) -> None:

    df = df_gsd_stats.copy()

    df["label"] = df["components"].map(surge_labels)

    groups = df.groupby("label")
    labels = list(groups.groups.keys())

    fig, ax = plt.subplots(figsize=(8, 8))

    for i, (name, group) in enumerate(groups, start=1):
        color = surge_colors.get(name, "black")  # default black if not found

        # jitter for visibility
        x_jitter = np.random.normal(i, 0.05, size=len(group))

        sizes = np.sqrt(group["number of tracks"].to_numpy()) * 4
        sizes = np.clip(sizes, 20, 300)

        # --- d95 points (slightly shifted) ---
        ax.scatter(
            x_jitter,
            group["d95"],
            s=sizes,
            alpha=0.8,
            color=color,
            marker="s",
            label=f"d95" if i == 2 else None
        )

        # --- d50 points ---
        ax.scatter(
            x_jitter,
            group["d50"],
            s=sizes,
            alpha=0.8,
            color=color,
            label=f"d50" if i == 2 else None
        )



        # --- median lines ---
        ax.hlines(
            group["d50"].median(),
            i - 0.3,
            i + 0.3,
            linewidth=2,
            linestyles="dashed",
            color=color,
            label= 'Median' if i == 2 else None
        )

        ax.hlines(
            group["d95"].median(),
            i - 0.3,
            i + 0.3,
            linewidth=2,
            linestyles="dashed",
            color=color
        )

    # --- formatting ---
    ax.set_xticks(range(1, len(labels) + 1))
    ax.tick_params(axis='both', labelsize=14)
    ax.set_xticklabels(labels, fontsize=14)
    ax.set_ylabel("Grain size (m)", fontsize=14)
    ax.set_xlabel("Component Classes", fontsize=14)

    ax.legend(frameon=False,
              fontsize=12,
              loc='best',
              facecolor="white",
              edgecolor="black",
              framealpha=1)


    fig_name = f'GSD_surge_type_compare_{config.EVENT}'
    output_dir_for_plots = Path(config.OUTPUT_DIR)
    output_path = Path(output_dir_for_plots) / fig_name
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)