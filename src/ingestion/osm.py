import osmnx as ox
import geopandas as gpd

from src.utils.io import save_geodataframe
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


# download points of interest from OpenStreetMap for a city
def ingest_pois(place_name: str, output_path: str) -> gpd.GeoDataFrame:
    tags = {
        "amenity": ["school", "hospital", "clinic", "pharmacy"],
        "leisure": ["park"],
        "shop": True
    }

    logger.info("Downloading POIs for %s", place_name)
    gdf = ox.features_from_place(place_name, tags=tags)

    gdf = gdf.reset_index()
    logger.info("Downloaded %s POI records", len(gdf))

    save_geodataframe(gdf, output_path)
    logger.info("Saved raw POIs to %s", output_path)

    return gdf