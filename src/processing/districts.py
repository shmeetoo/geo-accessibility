import geopandas as gpd

from src.utils.io import save_geodataframe
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

POSSIBLE_NAME_COLUMNS = [
    "district_name",
    "name", 
    "nazwa",
    "NAME",
    "JPT_NAZWA_",
    "dzielnica"
]

def _find_district_name_column(gdf: gpd.GeoDataFrame) -> str:
    for col in POSSIBLE_NAME_COLUMNS:
        if col in gdf.columns:
            return col
    
    raise ValueError(
        f"Could not find district name column. Available columns: {list(gdf.columns)}"
    )

def process_districts(input_path: str, output_path: str) -> gpd.GeoDataFrame:
    logger.info("Reading raw data from %s", input_path)
    gdf = gpd.read_file(input_path)

    logger.info("Loaded %s district rows", len(gdf))

    # select column with district name
    name_col = _find_district_name_column(gdf)
    logger.info("Using district name column: %s", name_col)

    # remove city boundaries data
    gdf = gdf[gdf[name_col] != "Warszawa"]

    # use only district_name and geometry columns
    gdf = gdf[[name_col, "geometry"]].copy()
    gdf = gdf.rename(columns={name_col: "district_name"})

    # skip spaces
    gdf["district_name"] = gdf["district_name"].astype(str).str.strip()

    # set / change CRS to EPSG:4326
    if gdf.crs is None:
        logger.warning("Districts CRS is missing, assuming EPSG:4326")
        gdf = gdf.set_crs(epsg=4326)
    else:
        gdf = gdf.to_crs(epsg=4326)

    # skip faulty geometry
    gdf = gdf[gdf.geometry.notnull()].copy()
    gdf = gdf[gdf.is_valid].copy()

    logger.info("Processed district rows after cleaning: %s", len(gdf))
    save_geodataframe(gdf, output_path)
    logger.info("Saved processed districts to %s", output_path)

    return gdf