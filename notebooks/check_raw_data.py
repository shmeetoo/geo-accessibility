import pandas as pd
import geopandas as gpd

districts = gpd.read_file("data/raw/districts/warsaw_districts.geojson")
pois = gpd.read_file("data/raw/pois/warsaw_pois.geojson")
population = pd.read_csv("data/raw/population/warsaw_population.csv")
transport = gpd.read_file("data/raw/transport/warsaw_stops.geojson")

print("DISTRICTS:", districts.shape)
print(districts.head())

print("POIs:", pois.shape)
print(pois.head())

print("POPULATION:", population.shape)
print(population.head())

print("TRANSPORT:", transport.shape)
print(transport.head())