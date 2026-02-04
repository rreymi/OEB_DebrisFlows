# =============================================================================
# Project:        GSD OEB
# Script:         Main Script for Track Filtering and Data Visualization
# Author:         Roman Renner
# Date:           2026-01-28
# Description:    Script to Filter Tracks, Determine velocities and grain sizes
#                 and visualize data in simple plots
# =============================================================================

# ------------------------------
# Import Libraries
# ------------------------------
from OEB_Filter_process import filter_process
from OEB_Calculations import calculate_vel
from OEB_Plotting import plot_stats, plot_grainsize
from OEB_GSD import calculate_gsd

# ------------------------------
# Configuration / Parameters # import config --> CHECK CONFIG
# ------------------------------
import config
config.START_FRAME = 50000
config.END_FRANE = 72500

# ------------------------------
# Run options
# ------------------------------
Run_Filter = False
Run_Calculations = True
Run_Visualization = True
Run_GSD = True

# Calculation ---
run_calc_per_frame = True
run_calc_per_track = True

# Plotting ---
plot_stats_per_frame = True
plot_stats_per_track = True
plot_xy_mov_for_frame_sequence = True


def main():

    if Run_Filter:
        plot_xy_movement = True
        filter_process(plot_xy_movement)

    if Run_Calculations:
        calculate_vel(run_calc_per_frame, run_calc_per_track)

    if Run_Visualization:
        plot_stats(plot_stats_per_frame, plot_stats_per_track, plot_xy_mov_for_frame_sequence)

    if Run_GSD:
        df_per_track_grainsize, df_grainsize_lowess = calculate_gsd()
        plot_grainsize(df_per_track_grainsize, df_grainsize_lowess)

if __name__ == "__main__":
    main()