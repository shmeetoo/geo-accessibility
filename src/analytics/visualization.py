import os
import geopandas as gpd
import plotly.express as px
from src.db.connection import get_engine


def create_district_choropleth(metric: str, title: str, output_file: str):
    engine = get_engine()

    # select desired columns
    query = """
    SELECT d.district_name, d.geometry, f.population, f.area_km2, 
        f.population_density, f.poi_count, f.transport_count
    FROM districts d
    JOIN district_features f
    ON d.district_name = f.district_name
    """

    gdf = gpd.read_postgis(query, engine, geom_col="geometry")
    # change CRS just in case
    gdf.to_crs(epsg=4326)

    # geojson for plotly
    geojson = gdf.__geo_interface__

    # create choropleth
    fig = px.choropleth_map(
        gdf,
        geojson=geojson,
        locations=gdf.index,
        color=metric,
        hover_name="district_name",
        hover_data={
            "population": True,
            "area_km2": ":.2f",
            "population_density": ":.2f",
            "poi_count": True,
            "transport_count": True
        },
        center={"lat": 52.2297, "lon": 21.0122},
        map_style="carto-positron",
        zoom=10,
        opacity=0.6,
        title=title
    )

    # create report forlder if not exists
    os.makedirs("reports", exist_ok=True)
    output_path = f"reports/{output_file}"
    fig.write_html(output_path)

    print(f"Map saved to {output_path}")

if __name__ == "__main__":
    create_district_choropleth(
        metric="population_density",
        title="Population density by district",
        output_file="population_density_map.html"
    )

    create_district_choropleth(
        metric="poi_count",
        title="POI count by district",
        output_file="poi_count_map.html"
    )

    create_district_choropleth(
        metric="transport_count",
        title="Transport stops by district",
        output_file="transport_count_map.html"
    )