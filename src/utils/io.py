from pathlib import Path
import pandas as pd
import geopandas as gpd

# ensure that parent directory exists
def ensure_parent_dir(file_path: str) -> None:
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)

# save as csv
def save_dataframe(df: pd.DataFrame, file_path: str) -> None:
    ensure_parent_dir(file_path)
    df.to_csv(file_path, index=False)

# save as geojson
def save_geodataframe(gdf: gpd.GeoDataFrame, file_path: str) -> None:
    ensure_parent_dir(file_path)
    gdf.to_file(file_path, driver="GeoJSON")