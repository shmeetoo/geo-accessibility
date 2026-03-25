from src.processing.districts import process_districts
from src.processing.pois import process_pois
from src.processing.population import process_population
from src.processing.transport import process_transport
from src.utils.config import load_config

def main() -> None:
    config = load_config()

    process_districts(
        input_path=config["files"]["districts_raw"],
        output_path=config["files"]["districts_processed"]
    )

    process_pois(
        input_path=config["files"]["pois_raw"],
        output_path=config["files"]["pois_processed"]
    )

    process_population(
        input_path=config["files"]["population_raw"],
        output_path=config["files"]["population_processed"]
    )

    process_transport(
        input_path=config["files"]["transport_raw"],
        output_path=config["files"]["transport_processed"]
    )

if __name__ == "__main__":
    main()