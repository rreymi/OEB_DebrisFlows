# =============================================================================
# Project:        GSD OEB
# Script:         Main Script for Track Filtering and Data Visualization
# Author:         Roman Renner
# Date:           2026-02-13
# Description:    Script to Filter Tracks, Determine velocities and grain sizes
#                 and visualize data in simple plots
# =============================================================================

# ------------------------------
# Import Libraries
# ------------------------------
from OEB_Filter_process import filter_process
from OEB_Calculations import calculate_vel, calculate_gs
from OEB_Plotting import plot_stats, plot_grainsize, plot_cross_section
from OEB_Model_performance import plot_detections


# ------------------------------
# Configuration / Parameters # import config --> CHECK CONFIG
# ------------------------------
import config
config.START_FRAME = 39000
config.END_FRAME = 41600

# ------------------------------
# Run options
# ------------------------------
Run_Filter = True                      # TrackFiles get filtered, filter para defined in config. Output: df_clean
Run_Calculations = True                # df_per_track_vel + grainsize and df_mova/df_stats get calc using df_clean
Run_Plotting = True                    # Visualize data

# ------------------------------
# --- Calculations ---
# Velocity
run_calc_Vel = True
run_calc_per_frame = True              # df_mova and df_stats (moving averages of per frame statistics)
run_calc_per_track = True              # lowess track velocity
# Grain SIze
run_calc_GS = True                     # lowess track grainsize

# ------------------------------
# --- Plotting ---
plot_stats_per_frame = True             # Per Frame stats (Moving Average plots)
plot_track_velocity = True              # Per Track stats (LOWESS Plot)
plot_track_grainsize = True             # Per Track stats (LOWESS + Bubble plot)
plot_xy_mov_for_frame_sequence = True   # X - Y Track movement
plot_cross_sec = True                   # Velocity cross-section plot
plot_number_of_detections = True        # Plot number of Detections (YOLO, tracking and after  filtering)



def main():

    if Run_Filter:
        filter_process()

    if Run_Calculations:
        if run_calc_Vel:
            calculate_vel(run_calc_per_frame, run_calc_per_track)
        if run_calc_GS:
            calculate_gs()

    if Run_Plotting:
        plot_stats(plot_stats_per_frame, plot_track_velocity, plot_xy_mov_for_frame_sequence)

        if plot_track_grainsize:
            plot_grainsize()

        if plot_cross_sec:
            plot_cross_section()

        if plot_number_of_detections:
            plot_detections()



    print('all done')
if __name__ == "__main__":
    main()