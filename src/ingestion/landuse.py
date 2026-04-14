import osmnx as ox
import geopandas as gpd

from src.utils.io import save_geodataframe
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

# download landuse data and save it to data/raw
def ingest_landuse(place_name: str, output_path: str) -> gpd.GeoDataFrame:
    tags = {
        "landuse": True,
        "leisure": True,
        "natural": True,
        "railway": True
    }

    logger.info("Downloading landuse data for %s", place_name)
    gdf = ox.features_from_place(place_name, tags=tags)

    gdf = gdf.reset_index()
    logger.info("Downloaded %s landuse data records", len(gdf))
    
    save_geodataframe(gdf, output_path)
    logger.info("Saved raw landuse data to %s", output_path)

    return gdf