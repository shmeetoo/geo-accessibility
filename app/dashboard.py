import dash
from dash import Input, Output, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

from app.data_loader import load_dashboard_data
from app.layout import create_layout


# load data on startup
gdf = load_dashboard_data()

# add accessibility score (simple weighted metric)
gdf["accessibility_score"] = (
    0.4 * gdf["poi_count"].fillna(0)
    + 0.4 * gdf["transport_count"].fillna(0)
    + 0.2 * gdf["population_density"].fillna(0) / 1000
)

# available metrics
METRIC_LABELS = {
    "population_density": "Population Density",
    "transport_count": "Transport Stops Count",
    "poi_count": "POI Count",
    "accessibility_score": "Accessibility Score"
}

metric_options = [
    {"label": label, "value": key}
    for label, key in METRIC_LABELS.items()
]

default_metric = "population_density"

# initialize dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Geo Accessibility Dashboard"
app.layout = create_layout(metric_options, default_metric)


# helper functions
def build_map(metric):
    geojson = gdf.__geo_interface__

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
            "transport_count": True,
            "accessibility_score": ":.2f"
        },
        center={"lat": 52.2297, "lon": 21.0122},
        map_style="carto-positron",
        zoom=10,
        opacity=0.7,
        title=f"{METRIC_LABELS[metric]} by District"
    )

    fig.update_layout(margin={"r":0, "t":50, "l":0, "b":0})
    return fig

def build_ranking(metric):
    ranking_df = gdf[["district_name", metric]].copy()
    ranking_df = ranking_df.sort_values(metric, ascending=False).head(10)

    fig = px.bar(
        ranking_df,
        x=metric,
        y="district_name",
        orientation="h",
        title=f"Top 10 Districts by{METRIC_LABELS[metric]}"
    )

    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return fig

def build_summary_card(selected_district):
    if selected_district is None:
        return dbc.Card(
            dbc.CardBody(
                [
                    html.H5("District Details", className="card-title"),
                    html.P("Click a districk on the map to see details.")
                ]
            )
        )
    
    row = gdf[gdf["district_name"] == selected_district].iloc[0]

    return dbc.Card(
        dbc.CardBody(
            [
                html.H4(row["district_name"], className="card-title"),
                html.Hr(),
                html.P(f"Population: {int(row['population'])}"),
                html.P(f"Area (km²): {row['area_km2']:.2f}"),
                html.P(f"Population Density: {row['population_density']:.2f}"),
                html.P(f"POI Count: {int(row['poi_count'])}"),
                html.P(f"Transport Stops: {int(row['transport_count'])}"),
                html.P(f"Accessibility Score: {row['accessibility_score']:.2f}")
            ]
        )
    )

# callbacks
@app.callback(
    Output("district-map", "figure"),
    Output("ranking-chart", "figure"),
    Input("metric-dropdown", "value")
)

def update_visuals(metric):
    return build_map(metric), build_ranking(metric)

@app.callback(
    Output("district-summary-card", "children"),
    Input("district-map", "clickData")
)

def update_summary(click_data):
    if click_data is None:
        return build_summary_card(None)
    
    point_index = click_data["points"][0]["location"]
    selected_district = gdf.iloc[point_index]["district_name"]

    return build_summary_card(selected_district)


# run app
if __name__ == "__main__":
    app.run(debug=True)