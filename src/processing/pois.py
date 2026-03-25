import pandas as pd
import geopandas as gpd

from src.utils.io import save_geodataframe
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

def classify_poi(row: pd.Series) -> str:
    amenity = row.get("amenity")
    leisure = row.get("leisure")
    shop = row.get("shop")

    if amenity == "school":
        return "education"
    if amenity in {"hospital", "clinic", "pharmacy"}:
        return "healthcare"
    if leisure == "park":
        return "green_area"
    if pd.notna(shop):
        return "retail"
    return "other"

def get_subcategory(row: pd.Series) -> str:
    for col in ["amenity", "leisure", "shop"]:
        value = row.get(col)
        if pd.notna(value):
            return str(value)
        
    return "unknown"


def process_pois(input_path: str, output_path: str) -> gpd.GeoDataFrame:
    logger.info("Reading raw POIs data from %s", input_path)
    gdf = gpd.read_file(input_path)

    logger.info("Loaded %s POI rows", len(gdf))

    # set / change CRS to EPSG:4326
    if gdf.crs is None:
        logger.warning("POIs CRS is missing, assuming EPSG:4326")
        gdf.set_crs(epsg=4326)
    else:
        gdf.to_crs(epsg=4326)

    # skip faulty geometry
    gdf = gdf[gdf.geometry.notnull()].copy()
    gdf = gdf[gdf.is_valid].copy()

    # check column names occurance
    if "name" not in gdf.columns:
        gdf["name"] = None
    if "amenity" not in gdf.columns:
        gdf["amenity"] = None
    if "leisure" not in gdf.columns:
        gdf["leisure"] = None
    if "shop" not in gdf.columns:
        gdf["shop"] = None

    # add poi_category and subcategory columns
    gdf["poi_category"] = gdf.apply(classify_poi, axis=1)
    gdf["subcategory"] = gdf.apply(get_subcategory, axis=1)

    # add POI id
    gdf = gdf.reset_index(drop=True)
    gdf["poi_id"] = gdf.index + 1

    # use only relevant columns
    gdf = gdf[["poi_id", "name", "poi_category", "subcategory", "geometry"]].copy()

    logger.info("Processed POI rows after cleaning: %s", len(gdf))
    save_geodataframe(gdf, output_path)
    logger.info("Saved processed POIs to %s", output_path)

    return gdf