import osmnx as ox
import geopandas as gpd

from src.utils.io import save_geodataframe
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


# download public transport stop-related features from OpenStreetMap
def ingest_transport_stops(place_name: str, output_path: str) -> gpd.GeoDataFrame:
    tags = {
        "highway": ["bus_stop"],
        "public_transport": ["platform", "stop_position"]
    }

    logger.info("Downloading transport stops for %s", place_name)
    gdf = ox.features_from_place(place_name, tags=tags)

    gdf = gdf.reset_index()
    logger.info("Downloaded %s transport stop records", len(gdf))

    save_geodataframe(gdf, output_path)
    logger.info("Saved raw transport stops to %s", output_path)

    return gdf