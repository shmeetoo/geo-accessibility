import pandas as pd
import geopandas as gpd

from src.db.connection import get_engine

def load_districts(path: str):
    print(f"Loading districts from: {path}")
    engine = get_engine()
    gdf = gpd.read_file(path)
    print(f"District rows: {len(gdf)}")
    gdf.to_postgis("districts", engine, if_exists="replace", index=False)

def load_pois(path: str):
    print(f"Loading POIs from: {path}")
    engine = get_engine()
    gdf = gpd.read_file(path)
    print(f"POIs rows: {len(gdf)}")
    gdf.to_postgis("pois", engine, if_exists="replace", index=False)

def load_transport(path: str):
    print(f"Loading transport from: {path}")
    engine = get_engine()
    gdf = gpd.read_file(path)
    print(f"Transport rows: {len(gdf)}")
    gdf.to_postgis("transport", engine, if_exists="replace", index=False)

def load_population(path: str):
    print(f"Loading population from: {path}")
    engine = get_engine()
    df = pd.read_csv(path)
    print(f"Population rows: {len(df)}")
    df.to_sql("population", engine, if_exists="replace", index=False)    