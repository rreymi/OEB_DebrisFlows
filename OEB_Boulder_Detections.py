# Script to quickly visualize and check the performance of the obj detection model

import logging
import config
import pandas as pd
from pathlib import Path

from utils.boulder_det_utils import (
    get_detection_counts_yolo
)

from utils.plot_utils import (
    plot_number_of_detections,
    plot_number_of_detections_yolo8,
    plot_number_of_detections_yolo8_and_tracking,
    plot_number_of_detections_tracked_and_filtered

)

def plot_detections() -> None:

    #  Determine detections of YOLOv8
    base_dir = Path(r"D:\roman\Documents\Daten_Masterarbeit\03_output_Detection_Tracking")
    output_file = base_dir / config.EVENT /  'detections' /  f"df_detections_yolo_{config.EVENT}.parquet"

    # Check if file exists
    if output_file.exists():
        logging.info(f"File already exists: {output_file}. Loading existing DataFrame.")
        df = pd.read_parquet(output_file)
    else:
        logging.info(f"File not found. Computing detection counts for event {config.EVENT}...")
        df = get_detection_counts_yolo(config.EVENT, base_dir)                                     # calc detections per frame
        df.to_parquet(output_file)
        logging.info(f"Saved DataFrame to {output_file}")


    df_time = pd.read_parquet(config.OUTPUT_DIR/ f"df_time_{config.EVENT}.parquet")
    df_clean = pd.read_parquet(config.OUTPUT_DIR / f"df_clean_{config.EVENT}.parquet")
    df_raw = pd.read_parquet(config.OUTPUT_DIR / f"df_raw_{config.EVENT}.parquet")

    plot_number_of_detections(df_clean, df_time, config)

    plot_number_of_detections_yolo8(df_clean=df_clean, df_counts_yolo=df, df_time=df_time, config=config)

    plot_number_of_detections_yolo8_and_tracking(df_clean=df_clean, df_counts_yolo=df,df_raw=df_raw, df_time=df_time, config=config,
                                                 legend_loc="upper right",
                                                 add_surge_classes=False,
                                                 legend_loc_surge="upper left",
    )

    plot_number_of_detections_tracked_and_filtered(df_clean=df_clean,df_raw=df_raw, df_time=df_time, config=config,
                                                   legend_loc="upper right",
                                                   add_surge_classes=False,
                                                   legend_loc_surge="upper left",
                                                   )

    logging.info("--- Detections per FRAME plots done --- \n")

