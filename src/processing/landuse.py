import pandas as pd
import geopandas as gpd

from src.utils.io import save_geodataframe
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

EXCLUDED_TYPES = [
    "park",
    "forest",
    "grass",
    "water",
    "river",
    "railway",
    "industrial",
    "reservoir"
]

def process_landuse(input_path: str, output_path: str) -> gpd.GeoDataFrame:
    logger.info("Reading raw landuse data from %s", input_path)
    gdf = gpd.read_file(input_path)

    logger.info("Loaded %s landuse rows", len(gdf))

    gdf = gdf.to_crs(epsg=4326)

    # choose of columns
    cols = ["geometry", "landuse", "leisure", "natural", "railway"]
    gdf = gdf[[c for c in cols if c in gdf.columns]]

    # combine to one column - type
    gdf["type"] = (
        gdf["landuse"]
        .fillna(gdf.get("leisure"))
        .fillna(gdf.get("natural"))
        .fillna(gdf.get("railway"))
    )
    
    gdf = gdf[["geometry", "type"]]
    gdf = gdf[gdf["type"].notna()]
    gdf = gdf[gdf["type"].isin(EXCLUDED_TYPES)]
    
    # keep polygons, remove rubbish data
    gdf = gdf[gdf.geometry.type.isin(["Polygon", "MultiPolygon"])]
    gdf = gdf[gdf.geometry.notnull()].copy()
    gdf = gdf[gdf.is_valid].copy()

    logger.info("Processed landuse data rows after cleaning: %s", len(gdf))
    save_geodataframe(gdf, output_path)
    logger.info("Saved processed landuse data to %s", output_path)

    return gdf
    