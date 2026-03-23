import pandas as pd
import config


# Grain Size Distribution

df_per_track_grainsize = pd.read_parquet(config.OUTPUT_DIR/ f"df_per_track_grainsize_{config.EVENT}.parquet")