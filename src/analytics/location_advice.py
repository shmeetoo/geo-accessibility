import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point
from src.db.connection import get_engine

# helpers
def normalize(series):
    if series.max() == series.min():
        return pd.Series([0.5] * len(series))
    return (series - series.min()) / (series.max() - series.min())

# generate grid with points for potential new poi locations
def generate_grid(district_geom):
    minx, miny, maxx, maxy = district_geom.bounds

    points = []
    x = minx
    while x <= maxx:
        y = miny
        while y <= maxy:
            point = Point(x, y)
            if district_geom.contains(point):
                points.append(point)
            y += 300 #grid size ~300m
        x += 300

    return gpd.GeoDataFrame(geometry=points, crs="EPSG:2178")


def compute_scores(grid, pois, transport, population_density):
    # distance to closest poi of the same category
    grid["dist_poi"] = grid.geometry.apply(
        lambda x: pois.distance(x).min() if not pois.empty else 0
    )

    # distance to transport
    grid["dist_transport"] = grid.geometry.apply(
        lambda x: transport.distance(x).min() if not transport.empty else 1000
    )

    # density (poi count in a 500m radius)
    def count_nearby(point, radius=500):
        return pois.distance(point).lt(radius).sum()
    
    grid["density"] = grid.geometry.apply(count_nearby)

    # additional scoring parameters
    # distance (gaussian sweet spot ~300-800m)
    grid["distance_score"] = grid["dist_poi"].apply(
        lambda x: np.exp(-((x - 500) ** 2) / (2 * 300 ** 2))
    )

    # density (sweet spot)
    grid["density_score"] = grid["density"].apply(
        lambda x: np.exp(-((x - 3) ** 2) / 5)
    )

    # transport score
    grid["transport_score"] = 1 / (1 + grid["dist_transport"])

    # demand
    grid["demand_score"] = population_density

    # normalization
    grid["distance_score"] = normalize(grid["distance_score"])
    grid["transport_score"] = normalize(grid["transport_score"])
    grid["density_score"] = normalize(grid["density_score"])

    # score
    grid["score"] = (
        0.3 * grid["distance_score"]
        + 0.2 * grid["density_score"]
        + 0.25 * grid["transport_score"]
        + 0.25 * grid["demand_score"]
    )

    return grid

def run_location_advice():
    engine = get_engine()

    # load data
    districts = gpd.read_postgis("SELECT * FROM districts", engine, geom_col="geometry")
    pois = gpd.read_postgis("SELECT * FROM pois", engine, geom_col="geometry")
    transport = gpd.read_postgis("SELECT * FROM transport", engine, geom_col="geometry")
    pop_density = pd.read_sql(
        "SELECT district_name, population_density FROM district_features",
        engine
    )
    districts = districts.merge(pop_density, on="district_name", how="left")

    # normlize density for proper score calculations
    pop_dens = pop_density["population_density"]
    pop_norm = (pop_dens - pop_dens.min()) / (pop_dens.max() - pop_dens.min())
    districts["pop_norm"] = pop_norm


    districts = districts.to_crs(epsg=2178)
    pois = pois.to_crs(epsg=2178)
    transport = transport.to_crs(epsg=2178)

    results = []

    categories = pois["poi_category"].dropna().unique()

    for district_name in districts["district_name"].unique():
        district_row = districts[districts["district_name"] == district_name].iloc[0]
        geom = district_row.geometry

        # limit poi and trasnport area to district boundaries
        pois_d = pois[pois.within(geom)].copy()
        transport_d = transport[transport.within(geom)].copy()

        if pois_d.empty:
            continue

        grid = generate_grid(geom)

        p_density = district_row["pop_norm"]

        for category in categories:
            pois_subset = pois_d[pois_d["poi_category"] == category]

            if pois_subset.empty:
                continue

            grid_scored = compute_scores(grid.copy(), pois_subset, transport_d, p_density)

            top = grid_scored.sort_values("score", ascending=False).head(3)

            for rank, (_, row) in enumerate(top.iterrows(), start=1):
                results.append({
                    "district_name": district_name,
                    "category": category,
                    "lat": row.geometry.y,
                    "lon": row.geometry.x,
                    "score": row.score,
                    "rank": rank
                })

    if not results:
        print("No results generated.")
        return

    gdf = gpd.GeoDataFrame(results, geometry="geometry", crs="EPSG:2178")
    gdf = gdf.to_crs(epsg=4326) #swap back to 4326 to eliminate location errors

    gdf.to_postgis(
        "district_poi_advice",
        engine,
        if_exists="replace",
        index=False
    )

    print("Location recommendations saved to DB")