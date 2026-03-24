import pandas as pd

from src.utils.io import save_dataframe
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

# load population data from local source csv and save it to the raw area
def ingest_population(source_path: str, output_path: str) -> pd.DataFrame:
    logger.info("Reading population data from %s", source_path)
    df = pd.read_csv(source_path)

    logger.info("Loaded %s population rows", len(df))
    save_dataframe(df, output_path)
    logger.info("Saved raw population data to %s", output_path)

    return df