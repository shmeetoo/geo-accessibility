import pandas as pd
import geopandas as gpd

from src.utils.io import save_geodataframe
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

def classify_stop_type(row: pd.Series) -> str:
    highway = row.get("highway")
    public_transport = row.get("public_transport")

    if highway == "bus_stop":
        return "bus_stop"
    if public_transport == "platform":
        return "platform"
    if public_transport == "stop_position":
        return "stop_position"
    return "other"

def process_transport(input_path: str, output_path: str) -> gpd.GeoDataFrame:
    logger.info("Reading raw transport stops data from %s", input_path)
    gdf = gpd.read_file(input_path)

    logger.info("Loaded %s transport rows", len(gdf))

    # set / change CRS to EPSG:4326
    if gdf.crs is None:
        logger.warning("Transport CRS is missing, assuming EPSG:4326")
        gdf.set_crs(epsg=4326)
    else:
        gdf.to_crs(epsg=4326)

    # skip faulty geometry
    gdf = gdf[gdf.geometry.notnull()].copy()
    gdf = gdf[gdf.is_valid].copy()

    # check column names occurance
    if "name" not in gdf.columns:
        gdf["name"] = None
    if "highway" not in gdf.columns:
        gdf["highway"] = None
    if "public_transport" not in gdf.columns:
        gdf["public_transport"] = None

    # add stop type
    gdf["stop_type"] = gdf.apply(classify_stop_type, axis=1)

    # add stop id
    gdf = gdf.reset_index(drop=True)
    gdf["stop_id"] = gdf.index + 1

    # use only relevant columns
    gdf = gdf[["stop_id", "name", "stop_type", "geometry"]].copy()

    logger.info("Processed transport rows after cleaning: %s", len(gdf))
    save_geodataframe(gdf, output_path)
    logger.info("Saved processed transport data to %s", output_path)

    return gdf