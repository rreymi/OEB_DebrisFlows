# Script to quickly visualize and check the performance of the obj detection model

import logging
import config
import pandas as pd
from pathlib import Path

from utils.model_performance_utils import (
    get_detection_counts_yolo, compute_detection_stats
)

from utils.plot_utils import (
    plot_number_of_detections,
    plot_number_of_detections_yolo8,
    plot_number_of_detections_yolo8_and_tracking

)

def plot_detections() -> None:

    event = config.EVENT


    #  Determine detections of YOLOv8
    base_dir = Path(r"D:\roman\Documents\Daten_Masterarbeit\03_output_Detection_Tracking")
    output_file = base_dir / event /  'detections' /  f"df_detections_yolo_{event}.parquet"

    # Check if file exists
    if output_file.exists():
        logging.info(f"File already exists: {output_file}. Loading existing DataFrame.")
        df = pd.read_parquet(output_file)
    else:
        logging.info(f"File not found. Computing detection counts for event {event}...")
        df = get_detection_counts_yolo(event, base_dir)                                     # calc detections per frame
        df.to_parquet(output_file)
        logging.info(f"Saved DataFrame to {output_file}")



    df_time = pd.read_parquet(config.OUTPUT_DIR/ f"df_time_{config.EVENT}.parquet")
    df_clean = pd.read_parquet(config.OUTPUT_DIR / f"df_clean_{config.EVENT}.parquet")
    df_raw = pd.read_parquet(config.OUTPUT_DIR / f"df_raw_{config.EVENT}.parquet")

    plot_number_of_detections(df_clean, df_time, config)

    plot_number_of_detections_yolo8(df_clean=df_clean, df_counts_yolo=df, df_time=df_time, config=config)

    plot_number_of_detections_yolo8_and_tracking(df_clean=df_clean, df_counts_yolo=df,df_raw=df_raw, df_time=df_time, config=config)

    print("--- Detections per FRAME plots done --- \n")

    # stats_df = compute_detection_stats(df)
