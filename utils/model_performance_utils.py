from pathlib import Path
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor



# -------------------------------
# Parallel file row counter
# -------------------------------
def _count_rows(path):
    with path.open("r") as f:
        return path.stem, sum(1 for _ in f)


# -------------------------------
# Main function (parallelized)
# -------------------------------
def get_detection_counts_yolo(event, base_dir, max_workers=8):
    base_dir = Path(base_dir)
    folder = base_dir / event / "detections" / "labels"

    if not folder.exists():
        raise FileNotFoundError(f"Folder does not exist: {folder}")

    files = list(folder.glob("*.txt"))

    data = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(tqdm(executor.map(_count_rows, files),
                            total=len(files),
                            desc=f"Processing {event}"))

    for stem, row_count in results:
        data.append({
            "frame_number_img": int(stem),
            "number_of_detections_yolo": row_count
        })

    df = pd.DataFrame(data)
    df = df.sort_values("frame_number_img").reset_index(drop=True)

    return df



def compute_detection_stats(df):
    """
    Compute summary statistics for detections per frame.
    """

    stats = {
        "total_frames": len(df),
        "total_detections": df["number_of_detections_yolo"].sum(),
        "mean_detections": df["number_of_detections_yolo"].mean(),
        "median_detections": df["number_of_detections_yolo"].median(),
        "max_detections": df["number_of_detections_yolo"].max(),
        "min_detections": df["number_of_detections_yolo"].min(),
        "std_detections": df["number_of_detections_yolo"].std(),
        "frames_with_detections": (df["number_of_detections_yolo"] > 0).sum(),
        "percent_frames_with_detections": (df["number_of_detections_yolo"] > 0).mean() * 100,
    }

    stats_df = pd.DataFrame([stats])
    return stats_df


