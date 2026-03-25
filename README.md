# Geo Accessibility

Portfolio project focused on geospatial data engineering and analytics.

## Tech stack
- Python
- Pandas / NumPy
- SQL
- PostgreSQL + PostGIS
- Docker
- Streamlit / Plotly Dash

## Project goal
Build an end-to-end data pipeline for urban accessibility analysis.

## Raw data ingestion
The project ingests:
- Warsaw district boundaries from a public boundary dataset,
- POIs from OpenStreetMap via OSMnx,
- district population from a public city/statistical source,
- transport stops from OpenStreetMap via OSMnx.

All raw data are stored in `data/raw/` and remain uncleaned until the processing stage.
Population data currently use district-level values for year 2019.

## Data processing
Raw datasets are cleaned and standardized into the `data/processed/` layer.

Main processing steps:
- standardizing district names,
- unifying coordinate reference systems to EPSG:4326,
- selecting relevant columns,
- validating geometries,
- classifying POIs into higher-level business categories,
- standardizing transport stop types.