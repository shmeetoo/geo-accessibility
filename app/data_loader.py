import pandas as pd
import geopandas as gpd
from src.db.connection import get_engine

# load district features from db
def load_dashboard_data():
    engine = get_engine()

    query = """
    SELECT d.district_name, d.geometry, f.population, f.area_km2, 
        f.population_density, f.poi_count, f.transport_count
    FROM districts d
    JOIN district_features f
    ON d.district_name = f.district_name
    """

    gdf = gpd.read_postgis(query, engine, geom_col="geometry")
    gdf.to_crs(epsg=4326)

    return gdf