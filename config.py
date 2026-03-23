from pathlib import Path

# --------------------------------------------
# --- Event details
# --------------------------------------------
EVENT_YEAR = "2024"
EVENT_MONTH = "06"
EVENT_DAY = "14"

EVENT = f"{EVENT_YEAR}_{EVENT_MONTH}_{EVENT_DAY}"

START_FRAME = 0
END_FRAME = 10000

# --------------------------------------------
# --- Output paths
# --------------------------------------------
OUTPUT_DIR = Path.cwd() / "output" / EVENT


# --------------------------------------------
# --- FILTER / SMOOTHING parameters
# --------------------------------------------
# Step 1
VELOCITY_RANGE = (0,10)
GRAINSIZE_RANGE = (0,3)

# Step 2
MIN_ROLL_WINDOW = 3
MAX_ROLL_WINDOW = 11

# Step 3
YAXIS_MIN_LENGTH = 0.3

# Step 4
JUMP_THRESHOLD = 1

# Step 5
MIN_MEDIAN_TRACK_VEL = 0.1


# --------------------------------------------
# --- Calculation parameters per frame stats
# --------------------------------------------
MOVING_AVERAGE_WINDOW_SIZE = 9
GAP_THRESHOLD = 400
MIN_NUM_DETECTIONS = 2 # clean frames with very low number of detections

# --------------------------------------------
# --- Calculation parameters per TRACK
# --------------------------------------------
LOWESS_ITERATIONS = 1
LOWESS_FRAME_WINDOW_SIZE = 20
LOWESS_GAP_THRESHOLD = 150
LOWESS_SEGMENT_LENGTH = 20

# --------------------------------------------
# --- Plot Parameters
# --------------------------------------------
FIG_SIZE = (14,7)           # 2:1
FIG_SIZE_TIME = (15,6)      # 2.5:1
FIG_SIZE_BUBBLE = (15,7)

YLIM_VELOCITY = (0, 5)
YLIM_GRAINSIZE = (0, 1)

# PER TRACK Plots
STATISTIC_TYPE = "mean" # or "median"

# Cross-section plots
Y_AXIS_START= 4
Y_AXIS_END = -4
X_LIM_AXIS_CS = (-10, 2)

# X - Y Track Mov Plot
X_LIM_AXIS = (-10, 2)
Y_LIM_AXIS = (-8, 8)


# Bubble plot (Grain size + Track Velocities)
BIN_WIDTH_BUBBLE = 3