from sqlalchemy import text
from src.db.connection import get_engine


def create_tables():
    engine = get_engine()

    with engine.connect() as conn:
        conn.execute(text("""
        CREATE EXTENSION IF NOT EXISTS postgis;
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS districts (
            district_id SERIAL PRIMARY KEY,
            district_name TEXT,
            geometry GEOMETRY(MULTIPOLYGON, 4326)
        );
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS population (
            district_name TEXT,
            population INTEGER,
            year INTEGER
        );
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS pois (
            poi_id INTEGER,
            name TEXT,
            poi_category TEXT,
            subcategory TEXT,
            geometry GEOMETRY(GEOMETRY, 4326)
        );
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS transport (
            stop_id INTEGER,
            name TEXT,
            stop_type TEXT,
            geometry GEOMETRY(GEOMETRY, 4326)
        );
        """))

        conn.commit()