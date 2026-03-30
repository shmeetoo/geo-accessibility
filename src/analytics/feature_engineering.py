import pandas as pd
import geopandas as gpd
from src.db.connection import get_engine
from sqlalchemy import text

engine = get_engine()

# load data from db
districts = gpd.read_postgis("SELECT * FROM districts", engine, geom_col="geometry")
pois = gpd.read_postgis("SELECT * FROM pois", engine, geom_col="geometry")
transport = gpd.read_postgis("SELECT * FROM transport", engine, geom_col="geometry")
population = pd.read_sql("SELECT * FROM population", engine)

# calculate number of POIs per district
pois_per_district = gpd.sjoin(pois, districts, how="inner", predicate="within")
poi_count = pois_per_district.groupby("district_name").size().reset_index(name="poi_count")

# merge with districts table
districts = districts.merge(poi_count, on="district_name", how="left")
districts["poi_count"] = districts["poi_count"].fillna(0).astype(int)

# calculate number of transport stops per district
transport_per_district = gpd.sjoin(transport, districts, how="inner", predicate="within")
transport_count = transport_per_district.groupby("district_name").size().reset_index(name="transport_count")

# merge with districts table
districts = districts.merge(transport_count, on="district_name", how="left")
districts["transport_count"] = districts["transport_count"].fillna(0).astype(int)

# merge with districts table
districts = districts.merge(population, on="district_name", how="left")
districts["population"] = districts["population"].fillna(0).astype(int)

# calculate population density per district
# change crs to planar units for proper calculations (EPSG:2178 best for central-east Poland)
districts["area_km2"] = districts.to_crs(epsg=2178).area / 1e6
districts["population_density"] = districts["population"] / districts["area_km2"]

# create analyrics table and save it do db
districts.drop(columns="geometry").to_sql("district_features", engine, if_exists="replace", index=False)
print("Created analytical table 'district_features'.")