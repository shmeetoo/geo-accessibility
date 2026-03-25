import pandas as pd

from src.utils.io import save_dataframe
from src.utils.logging_utils import get_logger
from src.processing.mappings import DISTRICT_NAME_MAPPING

logger = get_logger(__name__)

def process_population(input_path: str, output_path: str) -> pd.DataFrame:
    logger.info("Reading raw population data from %s", input_path)
    df = pd.read_csv(input_path)

    logger.info("Loaded %s population rows", len(df))

    # check for required columns
    required_columns = {"district", "population", "year"}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required population columns: {missing_columns}")
    
    # standardize district names
    df = df[list(required_columns)].copy()
    df["district"] = df["district"].astype(str).str.strip()
    df["district_name"] = df["district"].map(DISTRICT_NAME_MAPPING).fillna(df["district"])

    # convert numbers, drop na and duplicates
    df["population"] = pd.to_numeric(df["population"], errors="coerce")
    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    df = df.dropna(subset=["district_name", "population", "year"]).copy()

    df["population"] = df["population"].astype(int)
    df["year"] = df["year"].astype(int)

    df = df[["district_name", "population", "year"]].drop_duplicates().copy()

    logger.info("Processed population rows after cleaning: %s", len(df))
    save_dataframe(df, output_path)
    logger.info("Saved processed population data to %s", output_path)

    return df