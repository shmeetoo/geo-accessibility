import pandas as pd
import geopandas as gpd
from src.db.connection import get_engine

# load district features from db
def load_dashboard_data():
    engine = get_engine()

    query = """
    SELECT 
        d.district_name,
        d.geometry,
        f.population,
        f.area_km2, 
        f.population_density,
        f.poi_count,
        f.transport_count
    FROM districts d
    JOIN district_features f
    ON d.district_name = f.district_name
    """

    gdf = gpd.read_postgis(query, engine, geom_col="geometry")
    gdf.to_crs(epsg=4326)

    return gdf

def load_location_advice():
    engine = get_engine()

    query = """
    SELECT 
        district_name,
        category,
        lat,
        lon,
        score,
        rank
    FROM district_poi_advice
    """

    return pd.read_sql(query, engine)

def load_pois_for_map():
    engine = get_engine()

    query = """
    SELECT 
        d.district_name,
        p.poi_category,
        p.name,
        ST_Y(ST_Centroid(p.geometry)) AS lat,
        ST_X(ST_Centroid(p.geometry)) AS lon
    FROM pois p
    JOIN districts d
    ON ST_Within(p.geometry, d.geometry)
    """

    return pd.read_sql(query, engine)