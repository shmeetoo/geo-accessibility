import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point
from shapely.prepared import prep
from shapely.geometry import box
from src.db.connection import get_engine
from sqlalchemy import text

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
            y += 100 #grid size ~100m
        x += 100

    return gpd.GeoDataFrame(geometry=points, crs="EPSG:2178")

def build_urban_mask(landuse: gpd.GeoDataFrame, buffer_m=50):
    landuse = landuse.to_crs(epsg=2178)

    landuse["geometry"] = landuse.buffer(buffer_m)

    union = landuse.geometry.union_all()

    return prep(union)

def filter_to_urban(grid: gpd.GeoDataFrame, urban_mask):
    if urban_mask is None:
        return grid
    
    mask = grid.geometry.apply(lambda x: urban_mask.intersects(x))
    return grid[mask].copy()

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
    grid["distance_score"] = np.exp(-((grid["dist_poi"] - 400) ** 2) / (2 * 250 ** 2))

    # hard penalty for "empty" places
    grid.loc[
        grid["dist_poi"] > 1200, "distance_score"
    ] *= 0.2

    # density (sweet spot)
    grid["density_score"] = np.exp(-((grid["density"] - 3) ** 2) / 5)
    
    # hard penalty for "empty" places
    grid.loc[
        grid["density"] == 0, "density_score"
    ]  *= 0.1

    # transport score (sweet spot)
    grid["transport_score"] = np.exp(-((grid["dist_transport"] - 200) ** 2) / (2 * 150 ** 2))

    # demand
    grid["demand_score"] = population_density

    # normalization
    grid["distance_score"] = normalize(grid["distance_score"])
    grid["transport_score"] = normalize(grid["transport_score"])
    grid["density_score"] = normalize(grid["density_score"])

    # score
    grid["score"] = (
        0.30 * grid["distance_score"] +
        0.25 * grid["density_score"] +
        0.25 * grid["transport_score"] +
        0.20 * grid["demand_score"]
    )

    # remove potential duplicates within top3 points
    grid["score"] += np.random.normal(0, 1e-6, len(grid))

    grid.loc[
        (grid["dist_transport"] > 300) & (grid["density"] == 0),
        "score"
    ] *= 0.1

    return grid

def select_top_k_with_spacing(gdf, k=3, min_dist=300):
    selected = []

    for _, row in gdf.sort_values("score", ascending=False).iterrows():
        point = row.geometry

        if all(point.distance(sel.geometry) >= min_dist for sel in selected):
            selected.append(row)

        if len(selected) == k:
            break

    return gpd.GeoDataFrame(selected, crs=gdf.crs)

def run_location_advice():
    engine = get_engine()

    # load data
    districts = gpd.read_postgis("SELECT * FROM districts", engine, geom_col="geometry")
    pois = gpd.read_postgis("SELECT * FROM pois", engine, geom_col="geometry")
    pois = pois[pois["poi_category"] != "green_area"]
    transport = gpd.read_postgis("SELECT * FROM transport", engine, geom_col="geometry")
    landuse = gpd.read_postgis("SELECT * FROM landuse", engine, geom_col="geometry")
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
    landuse = landuse.to_crs(epsg=2178)

    urban_mask = build_urban_mask(landuse, buffer_m=10)
    historic = landuse[landuse["historic"].notna()]
    historic_union = historic.geometry.union_all()

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
        grid = grid[~grid.geometry.intersects(historic_union)]
        grid = filter_to_urban(grid, urban_mask)

        p_density = district_row["pop_norm"]

        for category in categories:
            pois_subset = pois_d[pois_d["poi_category"] == category]

            if pois_subset.empty:
                continue

            grid_scored = compute_scores(grid.copy(), pois_subset, transport_d, p_density)

            top = select_top_k_with_spacing(grid_scored, k=3, min_dist=300)

            for rank, (_, row) in enumerate(top.iterrows(), start=1):
                results.append({
                    "district_name": district_name,
                    "category": category,
                    "score": row.score,
                    "rank": rank,
                    "geometry": row.geometry
                })

    if not results:
        print("No results generated.")
        return

    gdf = gpd.GeoDataFrame(results, geometry="geometry", crs="EPSG:2178")
    gdf = gdf.to_crs(epsg=4326) #swap back to 4326 to eliminate location errors

    gdf["lat"] = gdf.geometry.y
    gdf["lon"] = gdf.geometry.x

    gdf.to_postgis(
        "district_poi_advice",
        engine,
        if_exists="replace",
        index=False
    )

    # spatial index for faster calculations
    with engine.connect() as conn:
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_adv_geom ON district_poi_advice USING GIST (geometry);"
        ))

    print("Location recommendations saved to DB")

run_location_advice()