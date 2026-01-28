# =============================================================================
# Project:        GSD OEB
# Script:         Main Script for Track Filtering and Data Visualization
# Author:         Roman Renner
# Date:           2026-01-28
# Description:    This script loads the filtered track data, optionally runs
#                 the filtering pipeline, performs analyses, and visualizes
#                 track velocities, PIV velocities, and smoothed trends.
#                 Event and filter parameters are configured via config.py.
# =============================================================================

# ------------------------------
# Import Libraries
# ------------------------------
from DataVisualization_Filter_process import filter_process
from DataVisualization_Calculations import calculate_stats
from DataVisualization_Plotting import plot_stats


# ------------------------------
# Configuration / Parameters
# ------------------------------
# import config



# ------------------------------
# Run options
# ------------------------------

Run_Filter = False
Run_Calculations = True
Run_Visualization = True

# Basic parameters
start_frame = 50000
end_frame = 72500

# Plotting
plot_stats_per_frame = True
plot_stats_per_track = True



def main():

    if Run_Filter:
        filter_process()

    if Run_Calculations:
        calculate_stats(run_calc_per_frame = False, run_calc_per_track = True)

    if Run_Visualization:
        plot_stats(start_frame, end_frame, plot_stats_per_frame, plot_stats_per_track)


if __name__ == "__main__":
    main()