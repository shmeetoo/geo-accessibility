import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

# check env variables
def _get_required_env(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value:
        raise ValueError(f"Missing required environment variable: {var_name}")
    return value

# get env variables, create connection string, create engine
def get_engine():
    db_name = _get_required_env("POSTGRES_DB")
    db_user = _get_required_env("POSTGRES_USER")
    db_password = _get_required_env("POSTGRES_PASSWORD")
    db_host = os.getenv("POSTGRES_HOST", "localhost")
    db_port = os.getenv("POSTGRES_PORT", "5432")

    connection_string = (
        f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )

    return create_engine(connection_string)