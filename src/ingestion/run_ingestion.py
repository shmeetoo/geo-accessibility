from src.ingestion.districts import ingest_districts
from src.ingestion.osm import ingest_pois
from src.ingestion.population import ingest_population
from src.ingestion.transport import ingest_transport_stops
from src.utils.config import load_config

def main() -> None:
    config = load_config()

    ingest_districts(
        source_path="data/source/districts_source.geojson",
        output_path=config["files"]["districts_raw"]
    )

    ingest_pois(
        place_name="Warsaw, Poland",
        output_path=config["files"]["pois_raw"]
    )

    ingest_population(
        source_path="data/source/warsaw_population_source.csv",
        output_path=config["files"]["population_raw"]
    )

    ingest_transport_stops(
        place_name="Warsaw, Poland",
        output_path=config["files"]["transport_raw"]
    )

if __name__ == "__main__":
    main()