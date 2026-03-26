from src.utils.config import load_config
from src.db.schema import create_tables
from src.db.load_data import (
    load_districts,
    load_pois,
    load_population,
    load_transport
)

def main() -> None:
    config = load_config()

    print("Creating database schema...")
    create_tables()

    print("Loading districts...")
    load_districts(config["files"]["districts_processed"])

    print("Loading POIs...")
    load_pois(config["files"]["pois_processed"])

    print("Loading population...")
    load_population(config["files"]["population_processed"])

    print("Loading transport...")
    load_transport(config["files"]["transport_processed"])

    print("Database loading completed successfully.")

if __name__ == "__main__":
    main()