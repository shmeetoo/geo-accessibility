import pandas as pd
import geopandas as gpd

districts = gpd.read_file("data/processed/districts/warsaw_districts.geojson")
pois = gpd.read_file("data/processed/pois/warsaw_pois.geojson")
population = pd.read_csv("data/processed/population/warsaw_population.csv")
transport = gpd.read_file("data/processed/transport/warsaw_stops.geojson")

print("DISTRICTS")
print(districts.info())
print(districts.head(), "\n")

print("POIS")
print(pois.info())
print(pois.head(), "\n")

print("POPULATION")
print(population.info())
print(population.head(), "\n")

print("TRANSPORT")
print(transport.info())
print(transport.head(), "\n")