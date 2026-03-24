# Data sources

## 1. District boundaries
Source: Warsaw open data / official city boundaries dataset or another public GeoJSON dataset with district polygons.
Format: GeoJSON
Usage: district-level spatial aggregation and joins.

## 2. POIs
Source: OpenStreetMap via OSMnx
Method: Python script using osmnx.features_from_place("Warsaw, Poland", tags=...)
Format: GeoJSON
Usage: counting amenities and accessibility metrics.

## 3. Population
Source: public Warsaw district population table (official city page / statistical publication).
Format: CSV
Usage: normalization of accessibility indicators per district.

## 4. Transport stops
Source: OpenStreetMap via OSMnx
Method: Python script using osmnx.features_from_place("Warsaw, Poland", tags=...)
Format: GeoJSON
Usage: public transport accessibility metrics.
