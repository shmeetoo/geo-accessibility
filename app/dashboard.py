import dash
from dash import Input, Output, State, html, ALL, ctx, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import os
import pandas as pd
import geopandas as gpd
import numpy as np
from functools import lru_cache

from app.layout import create_layout
from app.data_loader import (
    load_dashboard_data,
    load_location_advice,
    load_pois_for_map
)

# load data on startup
gdf = load_dashboard_data()
df_advice = load_location_advice()
df_pois_map = load_pois_for_map()

GEOJSON = gdf.__geo_interface__

# min-max normalization
def normalize(series: pd.Series) -> pd.Series:
    if series.max() == series.min():
        return pd.Series([0.5] * len(series), index=series.index)
    return (series - series.min()) / (series.max() - series.min())

# accessibility score components
trans_access = 1 - np.exp(-gdf["transport_count"] / gdf["transport_count"].quantile(0.75))
poi_access = normalize(np.log1p(gdf["poi_count"]))
poi_per_capita = gdf["poi_count"] / gdf["population"]
trans_per_capita = gdf["transport_count"] / gdf["population"]

# add accessibility score (simple weighted metric)
gdf["accessibility_score"] = (
    0.45 * trans_access +
    0.35 * poi_access +
    0.10 * normalize(trans_per_capita) +
    0.10 * normalize(poi_per_capita)
)

# available metrics
METRICS = {
    "accessibility_score": "Accessibility Score",
    "population_density": "Population Density",
    "poi_count": "POI Count",
    "transport_count": "Transport Stops Count"
}

metric_options = [
    {"label": label, "value": value}
    for value, label in METRICS.items()
]

default_metric = "accessibility_score"

district_options = [
    {"label": district, "value": district}
    for district in sorted(gdf["district_name"].dropna().unique())
]

# KPI values
best_district = gdf.loc[gdf["accessibility_score"].idxmax(), "district_name"]

kpis = {
    "district_count": f"{gdf['district_name'].nunique()}",
    "avg_density": f"{gdf['population_density'].mean():.0f}",
    "total_pois": f"{int(gdf['poi_count'].sum()):}",
    "total_transport": f"{int(gdf['transport_count'].sum()):}",
    "best_district": best_district
}

# initialize dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True
)
app.title = "Geo Accessibility Dashboard"
app.layout = create_layout(metric_options, default_metric, district_options, kpis)


# helper functions
def apply_common_figure_style(fig):
    fig.update_layout(
        height=325,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Arial, sans-serif",
            size=13,
            color="#0f172a"
        ),
        margin=dict(l=5, r=5, t=5, b=5)
    )
    return fig

def build_district_map(metric, selected_district=None, district_a=None, district_b=None):
    fig = px.choropleth_map(
        gdf,
        geojson=GEOJSON,
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
        zoom=9,
        opacity=0.8,
    )

    fig.update_traces(
        marker_line_width=1.0,
        marker_line_color="white",
        hovertemplate="<b>%{hovertext}</b><br>Score: %{z:.2f}<extra></extra>"
    )

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar=dict(
            title=METRICS[metric],
            title_side="right",
            thickness=14,
            len=0.75,
            x=1.02
        )
    )

    if selected_district:
        selected_geom = gdf[gdf["district_name"] == selected_district]

        for _, row in selected_geom.iterrows():
            geom = row.geometry

            if geom.geom_type == "Polygon":
                geoms = [geom]
            else:
                geoms = geom.geoms

            for poly in geoms:
                x, y = poly.exterior.coords.xy
                fig.add_trace(go.Scattermap(
                    lon=list(x),
                    lat=list(y),
                    mode="lines",
                    line=dict(width=3, color="#ef4444"),
                    hoverinfo="skip",
                    showlegend=False
                ))

    def add_highlight(fig, district_name, color):
        if not district_name:
            return
        
        district_geom = gdf[gdf["district_name"] == district_name]
        
        for _, row in district_geom.iterrows():
            geom = row.geometry

            if geom.geom_type == "Polygon":
                geoms = [geom]
            else:
                geoms = geom.geoms

            for poly in geoms:
                x, y = poly.exterior.coords.xy
                fig.add_trace(go.Scattermap(
                    lon=list(x),
                    lat=list(y),
                    mode="lines",
                    line=dict(width=3, color=color),
                    hoverinfo="skip",
                    showlegend=False
                ))

    add_highlight(fig, district_a, "#2563eb")
    add_highlight(fig, district_b, "#f59e0b")

    return fig

@lru_cache(maxsize=32)
def build_ranking(metric):
    ranking_df = gdf[["district_name", metric]].copy()
    ranking_df = ranking_df.sort_values(metric, ascending=False).head(10)

    fig = px.bar(
        ranking_df,
        x=metric,
        y="district_name",
        orientation="h",
        color_discrete_sequence=["#4ea4a1"]
    )

    fig.update_traces(
        textposition="outside",
        marker_line_width=0
    )

    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        xaxis_title=METRICS[metric],
        yaxis_title="District"
    )
    return apply_common_figure_style(fig)

@lru_cache(maxsize=32)
def build_distribution(metric):
    fig = px.histogram(
        gdf,
        x=metric,
        nbins=12,
        color_discrete_sequence=["#4ea4a1"]
    )

    fig.update_layout(
        xaxis_title=METRICS[metric],
        yaxis_title="Number of Districts",
        bargap=0.08
    )
    return apply_common_figure_style(fig)

def build_insights_panel(selected_district):
    if not selected_district:
        return dbc.Alert([
            html.Div("No district selected", className="fw-semibold"),
            html.Div("Click on the map to explore insights.", className="small"),
        ], color="light", className="rounded-4 border-0")
    
    row = gdf[gdf["district_name"] == selected_district].iloc[0]

    def mini_card(label, value):
        return dbc.Card(
            dbc.CardBody([
                html.Div(label, className="text-muted small mb-1"),
                html.H4(value, className="fw-bold mb-0", style={"color": "#0f172a"})
            ], 
            ),
            className="border-0 rounded-4 h-100",
            style={
                "backgroundColor": "#f8fafc",
            }
        )

    return dbc.Row([
        dbc.Col(mini_card("District", row["district_name"]), md=6),
        dbc.Col(mini_card("Accessibility Score", f"{row['accessibility_score']:.2f}"), md=6),
        dbc.Col(mini_card("Population", f"{int(row['population']):}"), md=4),
        dbc.Col(mini_card("Area (km²)", f"{row['area_km2']:.2f}"), md=4),
        dbc.Col(mini_card("Density", f"{row['population_density']:.0f}"), md=4),
        dbc.Col(mini_card("POIs", f"{int(row['poi_count'])}"), md=6),
        dbc.Col(mini_card("Transport Stops", f"{int(row['transport_count'])}"), md=6),
    ], className="g-3")

def comparison_bar_row(label, val_a, val_b):
    def normalize_pair(a, b):
        max_val = max(a, b)
        if max_val == 0:
            return 0.5, 0.5
        return a / max_val, b / max_val

    def fmt(val):
        if isinstance(val, float):
            return f"{val:.2f}"
        return val

    norm_a, norm_b = normalize_pair(val_a, val_b)

    return html.Div([
        html.Div([
            # A value (left)
            html.Div(
                fmt(val_a),
                style={"color": "#2563eb", "textAlign": "left"},
                className="fw-semibold"
            ),
            # label (center)
            html.Div(
                label,
                style={"textAlign": "center"},
                className="fw-semibold text-muted"
            ),
            # B value (right)
            html.Div(
                fmt(val_b),
                style={"color": "#f59e0b", "textAlign": "right"},
                className="fw-semibold"
            ),
        ],
        className="d-grid mb-1",
        style={"gridTemplateColumns": "1fr auto 1fr", "alignItems": "center"}
        ),

        # bars
        html.Div([
            html.Div(
                style={
                    "width": f"{norm_a * 100}%",
                    "backgroundColor": "#2563eb",
                    "height": "8px",
                }
            ),
            html.Div(
                style={
                    "width": f"{norm_b * 100}%",
                    "backgroundColor": "#f59e0b",
                    "height": "8px",
                }
            ),
        ], style={
            "display": "flex",
            "backgroundColor": "#e2e8f0",
            "borderRadius": "4px",
            "overflow": "hidden"
        })
    ], className="mb-3")

def build_comparison_panel(district_a, district_b):
    if not district_a or not district_b:
        return dbc.Alert([
            html.Div("No districts selected", className="fw-semibold"),
            html.Div("Select two districts from controls panel.", className="small"),
        ], color="light", className="rounded-4 border-0")
    
    row_a = gdf[gdf["district_name"] == district_a].iloc[0]
    row_b = gdf[gdf["district_name"] == district_b].iloc[0]

    return html.Div([
        # header
        html.Div([

            html.Div(
                district_a,
                style={"color": "#2563eb", "textAlign": "left"},
                className="fw-semibold"
            ),

            html.Div(
                "   ",
                style={"textAlign": "center", "color": "#94a3b8"},
                className="small"
            ),

            html.Div(
                district_b,
                style={"color": "#f59e0b", "textAlign": "right"},
                className="fw-semibold"
            ),

        ], className="d-grid mb-3", style={
            "gridTemplateColumns": "1fr auto 1fr"
        }),
        
        # bars
        comparison_bar_row("Population", row_a["population"], row_b["population"]),
        comparison_bar_row("Area (km²)", row_a["area_km2"], row_b["area_km2"]),
        comparison_bar_row("Population Density", row_a["population_density"], row_b["population_density"]),
        comparison_bar_row("POI Count", row_a["poi_count"], row_b["poi_count"]),
        comparison_bar_row("Transport Stops", row_a["transport_count"], row_b["transport_count"]),
        comparison_bar_row("Accessibility Score", row_a["accessibility_score"], row_b["accessibility_score"]),

    ])

def build_category_cards(district, selected_category=None):
    if not district:
        return dbc.Alert([
            html.Div("No district selected", className="fw-semibold"),
            html.Div("Click on the map to explore POI categories.", className="small"),
        ], color="light", className="rounded-4 border-0")
    
    df = df_advice[df_advice["district_name"] == district]
    categories = sorted(df["category"].unique())

    tooltip_items = [
        "Transport accessibility",
        "Distance to existing POIs",
        "Local POI density",
        "Population demand",
        "Land use filtering"
    ]

    cards = []
    for c in categories:
        active = (c == selected_category)

        wrapper_id = f"category-wrapper-{c}"

        card = html.Div(
            c,
            id={"type": "category-card", "index": c},
            className="w-100 text-center fw-semibold py-3 border-0 rounded-4",
            style={
                "cursor": "pointer",
                "backgroundColor": "#53aca9" if active else "#f8fafc",
                "color": "#0f172a",
                "fontSize": "18px",
                "transition": "all 0.15s ease"
            },
        )

        tooltip = dbc.Tooltip(
            html.Div([
                html.Div("Scoring factors:", className="fw-semibold mb-1"),
                html.Ul([html.Li(item) for item in tooltip_items], className="mb-0")
            ]),
            target=wrapper_id,
            placement="right",
            style={"fontSize": "12px"}
        )

        cards.append(html.Div([card, tooltip], id=wrapper_id))

    return dbc.Stack(cards, gap=3)

def build_advice_map(df, pois, district_geom):
    # advice map legend
    df = df.copy()
    df["label"] = df["rank"].map({
        1: "Best location",
        2: "Second best",
        3: "Third best"
    })

    df["size"] = df["rank"].map({
        1: 15,
        2: 10,
        3: 5
    })

    fig = px.scatter_map(
        df,
        lat="lat",
        lon="lon",
        color="label",
        size="size",
        hover_data={"score": True},
        zoom=11,
    )

    # district boundary
    for _, row in district_geom.iterrows():
        geom = row.geometry

        for polygon in geom.geoms:
            x, y = polygon.exterior.coords.xy
            fig.add_trace(go.Scattermap(
                lon=list(x),
                lat=list(y),
                mode="lines",
                line=dict(width=2.3, color="rgba(0,0,0,0.6)"),
                hoverinfo="skip",
                showlegend=False
            ))

    # POI as overlay
    poi_fig = px.scatter_map(
        pois,
        lat="lat",
        lon="lon",
        hover_name="name"
    )

    for trace in poi_fig.data:
        trace.marker.size = 6
        trace.marker.color = "gray"
        trace.name = "Existing POI"
        fig.add_trace(trace)

    fig.update_layout(
        legend_title_text="Recommendation Rank",
        map_style="carto-positron",
        margin=dict(l=0, r=0, t=0, b=0)
    )

    return fig

@lru_cache(maxsize=128)
def get_advice_data(district, category):
    df = df_advice[
        (df_advice["district_name"] == district) &
        (df_advice["category"] == category)
    ].copy()

    pois = df_pois_map[
        (df_pois_map["district_name"] == district) &
        (df_pois_map["poi_category"] == category)
    ].copy()
    
    district_geom = gdf[gdf["district_name"] == district]

    return df, pois, district_geom

# callbacks
@app.callback(
    Output("district-map", "figure"),
    Input("metric-dropdown", "value"),
    Input("selected-district", "data"),
    Input("district-a-dropdown", "value"),
    Input("district-b-dropdown", "value")
)
def update_map(metric, selected_district, district_a, district_b):
    return build_district_map(metric, selected_district, district_a, district_b)

@app.callback(
    Output("ranking-chart", "figure"),
    Output("distribution-chart", "figure"),
    Input("metric-dropdown", "value")
)
def update_charts(metric):
    return build_ranking(metric), build_distribution(metric)

@app.callback(
    Output("district-summary-card", "children"),
    Input("selected-district", "data")
)
def update_summary(selected_district):
    return build_insights_panel(selected_district)

@app.callback(
    Output("district-comparison-panel", "children"),
    Input("district-a-dropdown", "value"),
    Input("district-b-dropdown", "value")
)
def update_comparison(district_a, district_b):
    return build_comparison_panel(district_a, district_b)

@app.callback(
    Output("category-cards", "children"),
    Input("selected-district", "data"),
    Input("selected-category", "data")
)
def update_category_cards(district, selected_category):
    return build_category_cards(district, selected_category)

@app.callback(
    Output("selected-category", "data"),
    Input({"type": "category-card", "index": ALL}, "n_clicks"),
    Input("reset-category-btn", "n_clicks"),
    Input("selected-district", "data"),
    prevent_initial_call=True
)
def manage_selected_category(card_clicks, reset_clicks, selected_district):
    triggered = ctx.triggered_id

    if not selected_district:
        return None

    if triggered == "selected-district":
        return None

    if triggered == "reset-category-btn":
        return None

    if isinstance(triggered, dict) and triggered.get("type") == "category-card":
        return triggered.get("index")
        
    return dash.no_update

@app.callback(
    Output("reset-category-btn", "style"),
    Input("selected-district", "data")
)
def toggle_reset_btn(district):
    if district:
        return {"display": "block"}
    return {"display": "none"}

@app.callback(
    Output("advice-container", "children"),
    Input("selected-category", "data"),
    Input("selected-district", "data"),
)
def update_advice_map(category, district):
    if not district:
        return dbc.Alert([
            html.Div("No district selected", className="fw-semibold"),
            html.Div("Click on the map to explore POI categories.", className="small"),
        ], color="light", className="rounded-4 border-0")
    
    if not category:
        return dbc.Alert([
            html.Div("No POI category selected", className="fw-semibold"),
            html.Div("Click on the POI category to explore recommended locations.", className="small"),
        ], color="light", className="rounded-4 border-0")

    df, pois, district_geom = get_advice_data(district, category)

    return html.Div(
        dcc.Graph(
            figure=build_advice_map(df, pois, district_geom),
            config={"displayModeBar": False},
        ),
    )

@app.callback(
    Output("selected-district", "data"),
    Output("district-map", "clickData"),
    Input("district-map", "clickData"),
    Input("reset-district-btn", "n_clicks"),
    prevent_initial_call=True
)
def store_selected_district(click_data, reset_clicks):
    if ctx.triggered_id == "reset-district-btn":
        return None, None

    if not click_data:
        return None, None
    
    point_index = click_data["points"][0]["location"]
    district = gdf.iloc[point_index]["district_name"]
    return district, None

@app.callback(
    Output("district-a-dropdown", "options"),
    Output("district-b-dropdown", "options"),
    Input("district-a-dropdown", "value"),
    Input("district-b-dropdown", "value")
)
def update_dropdown_options(district_a, district_b):
    options_a = [
        {"label": d, "value": d}
        for d in gdf["district_name"].sort_values().unique()
        if d != district_b
    ]

    options_b = [
        {"label": d, "value": d}
        for d in gdf["district_name"].sort_values().unique()
        if d != district_a
    ]

    return options_a, options_b


# run app
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8050))
    app.run(debug=False, host="0.0.0.0", port=port)