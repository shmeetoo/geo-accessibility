import dash
from dash import Input, Output, html
import dash_bootstrap_components as dbc
import plotly.express as px
import os

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
    {"label": "Accessibility Score", "value": "accessibility_score"},
    {"label": "Population Density", "value": "population_density"},
    {"label": "POI Count", "value": "poi_count"},
    {"label": "Transport Stops Count", "value": "transport_count"}
]

default_metric = "accessibility_score"

district_options = [
    {"label": district, "value": district}
    for district in sorted(gdf["district_name"].dropna().unique())
]

# KPI values
best_district = (
    gdf.sort_values("accessibility_score", ascending=False).iloc[0]["district_name"]
)

kpis = {
    "district_count": f"{gdf['district_name'].nunique()}",
    "avg_density": f"{gdf['population_density'].mean():.0f}",
    "total_pois": f"{int(gdf['poi_count'].sum()):}",
    "total_transport": f"{int(gdf['transport_count'].sum()):}",
    "best_district": best_district
}

# initialize dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Geo Accessibility Dashboard"
app.layout = create_layout(metric_options, default_metric, district_options, kpis)


# helper functions
def apply_common_figure_style(fig):
    fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Arial, sans-serif",
            size=13,
            color="#0f172a"
        ),
        title_font=dict(
            size=18,
            color="#0f172a"
        ),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    return fig

def build_map(metric):
    geojson = gdf.__geo_interface__

    fig = px.choropleth_map(
        gdf,
        geojson=geojson,
        locations=gdf.index,
        color=metric,
        color_continuous_scale="Viridis",
        hover_name="district_name",
        hover_data={
            "population": True,
            "area_km2": ":.2f",
            "population_density": ":.0f",
            "poi_count": True,
            "transport_count": True,
            "accessibility_score": ":.2f"
        },
        center={"lat": 52.2297, "lon": 21.0122},
        map_style="carto-positron",
        zoom=10,
        opacity=0.8,
        title=f"{METRIC_LABELS[metric]} by District"
    )

    fig.update_traces(
        marker_line_width=1.2,
        marker_line_color="white"
    )

    fig.update_layout(
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        coloraxis_colorbar=dict(
            title=METRIC_LABELS[metric],
            thickness=14,
            len=0.75
        )
    )
    return apply_common_figure_style(fig)

def build_ranking(metric):
    ranking_df = gdf[["district_name", metric]].copy()
    ranking_df = ranking_df.sort_values(metric, ascending=False).head(10)

    fig = px.bar(
        ranking_df,
        x=metric,
        y="district_name",
        orientation="h",
        title=f"Top 10 Districts by {METRIC_LABELS[metric]}",
    )

    fig.update_traces(
        textposition="outside",
        marker_line_width=0
    )

    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        xaxis_title=METRIC_LABELS[metric],
        yaxis_title="District"
    )
    return apply_common_figure_style(fig)

def build_distribution(metric):
    fig = px.histogram(
        gdf,
        x=metric,
        nbins=12,
        title=f"Distribution of {METRIC_LABELS[metric]} Across Districts"
    )

    fig.update_layout(
        xaxis_title=METRIC_LABELS[metric],
        yaxis_title="Number of Districts",
        bargap=0.08
    )
    return apply_common_figure_style(fig)

def build_summary_card(selected_district):
    if selected_district is None:
        return dbc.Alert(
            "Click a district on the map to see detailed insights.",
            color="light",
            className="rounded-4 border-0"
        )
    
    row = gdf[gdf["district_name"] == selected_district].iloc[0]

    def mini_card(label, value):
        return dbc.Card(
            dbc.CardBody(
                [
                    html.Div(label, className="text-muted small mb-1"),
                    html.H4(value, className="fw-bold mb-0", style={"color": "#0f172a"})
                ]
            ),
            className="border-0 rounded-4 h-100",
            style={"backgroundColor": "#f8fafc"}
        )

    return dbc.Row(
        [
            dbc.Col(mini_card("District", row["district_name"]), md=6),
            dbc.Col(mini_card("Accessibility Score", f"{row['accessibility_score']:.2f}"), md=6),
            dbc.Col(mini_card("Population", f"{int(row['population']):}"), md=4),
            dbc.Col(mini_card("Area (km²)", f"{row['area_km2']:.2f}"), md=4),
            dbc.Col(mini_card("Density", f"{row['population_density']:.0f}"), md=4),
            dbc.Col(mini_card("POIs", f"{int(row['poi_count'])}"), md=6),
            dbc.Col(mini_card("Transport Stops", f"{int(row['transport_count'])}"), md=6),
        ],
        className="g-3"
    )

def build_comparison_panel(district_a, district_b):
    if not district_a or not district_b:
        return dbc.Alert(
            "Select two districts to compare.",
            color="light",
            className="rounded-4 border-0"
        )
    
    row_a = gdf[gdf["district_name"] == district_a].iloc[0]
    row_b = gdf[gdf["district_name"] == district_b].iloc[0]

    comparison_rows = [
        ("Population", int(row_a["population"]), int(row_b["population"])),
        ("Area (km²)", f"{row_a['area_km2']:.2f}", f"{row_b['area_km2']:.2f}"),
        ("Population Density", f"{row_a['population_density']:.0f}", f"{row_b['population_density']:.0f}"),
        ("POI Count", int(row_a["poi_count"]), int(row_b["poi_count"])),
        ("Transport Stops", int(row_a["transport_count"]), int(row_b["transport_count"])),
        ("Accessibility Score", f"{row_a['accessibility_score']:.2f}", f"{row_b['accessibility_score']:.2f}")
    ]

    table_header = html.Thead(
        html.Tr(
            [
                html.Th("Metric", style={"color": "#475569"}),
                html.Th(district_a, style={"color": "#0f172a"}),
                html.Th(district_b, style={"color": "#0f172a"})
            ]
        )
    )

    table_body = html.Tbody(
        [
            html.Tr(
                [
                    html.Td(metric, className="fw-semibold", style={"color": "#334155"}),
                    html.Td(val_a),
                    html.Td(val_b)
                ]
            )
            for metric, val_a, val_b in comparison_rows
        ]
    )

    return dbc.Table(
        [table_header, table_body],
        bordered=False,
        hover=True,
        responsive=True,
        className="align-middle"
    )


# callbacks
@app.callback(
    Output("district-map", "figure"),
    Output("ranking-chart", "figure"),
    Output("distribution-chart", "figure"),
    Input("metric-dropdown", "value")
)
def update_visuals(metric):
    return build_map(metric), build_ranking(metric), build_distribution(metric)

@app.callback(
    Output("district-summary-card", "children"),
    Input("district-map", "clickData")
)
def update_summary(click_data):
    if click_data is None:
        default_district = (
            gdf.sort_values("accessibility_score", ascending=False).iloc[0]["district_name"]
        )
        return build_summary_card(None)
    
    point_index = click_data["points"][0]["location"]
    selected_district = gdf.iloc[point_index]["district_name"]

    return build_summary_card(selected_district)

@app.callback(
    Output("district-comparison-panel", "children"),
    Input("district-a-dropdown", "value"),
    Input("district-b-dropdown", "value")
)
def update_comparison(district_a, district_b):
    return build_comparison_panel(district_a, district_b)

# run app
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8050))
    app.run(debug=False, host="0.0.0.0", port=port)