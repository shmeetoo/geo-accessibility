import geopandas as gpd

from src.utils.io import save_geodataframe
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

# load district boundaries from a local source
# save them to the project's raw data area
def ingest_districts(source_path: str, output_path: str) -> gpd.GeoDataFrame:
    logger.info("Reading district boundaries from %s", source_path)
    gdf = gpd.read_file(source_path)

    logger.info("Loaded %s district records", len(gdf))
    save_geodataframe(gdf, output_path)
    logger.info("Saved raw districts to %s", output_path)

    return gdf