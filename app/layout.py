from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

def create_kpi_card(title, value, subtitle=None, icon=None):
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    [
                        html.Div(
                            title, 
                            className="text-uppercase small fw-semibold",
                            style={"color": "#64748b", "letterSpacing": "0.04em"}
                        ),
                        html.Div(icon or "", className="fs-3")
                    ],
                    className="d-flex justify-content-between align-items-center mb-2"
                ),
                html.H2(
                    value, 
                    className="fw-bold mb-1",
                    style={"color": "#0f172a"}
                ),
                html.Div(
                    subtitle or "", 
                    className="small",
                    style={"color": "#94a3b8"}
                )
            ]
        ),
        className="shadow-sm border-0 rounded-4 h-100",
        style={
            "backgroundColor": "white",
            "transition": "all 0.2s ease-in-out"
        }
    )

def create_layout(metric_options, default_metric, district_options, kpis):
   return dbc.Container(
        [
            dcc.Store(id="selected-district"),
            dcc.Store(id="selected-category"),

            # hero header
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                "PORTFOLIO DATA PRODUCT",
                                className="text-uppercase small fw-bold mb-2",
                                style={"color": "#38bdf8", "letterSpacing": "0.08em"}
                            ),
                            html.H1(
                                "Geo Accessibility Dashboard",
                                className="fw-bold display-5 mb-3",
                                style={"color": "white"}
                            ),
                            html.P(
                                "District-level geospatial analytics platform for exploring urban accessibility, population concentration, public transport availability and POI density.",
                                className="fs-5 mb-3",
                                style={"color": "#cbd5e1", "maxWidth": "700px"}
                            ),
                            dbc.Badge(
                                "Interactive Geospatial Analytics",
                                className="px-3 py-2 fs-6 rounded-pill border-0",
                                style={
                                    "backgroundColor": "#0ea5e9",
                                    "color": "white"
                                }
                            )
                        ],
                        width=12
                    )
                ],
                className="mb-4 p-4 rounded-4 shadow-sm",
                style={
                    "background": "linear-gradient(135deg, #0f172a 0%, #1e293b 55%, #0f766e 100%)"
                }
            ),

            # kpi cards
            dbc.Row(
                [
                    dbc.Col(
                        create_kpi_card(
                            "Districts",
                            kpis["district_count"],
                            "Administrative units analyzed",
                            "🗺️"
                        ),
                        lg=2, md=4
                    ),
                    dbc.Col(
                        create_kpi_card(
                            "Avg Density",
                            kpis["avg_density"],
                            "People per km²",
                            "👥"
                        ),
                        lg=2, md=4
                    ),
                    dbc.Col(
                        create_kpi_card(
                            "Total POIs",
                            kpis["total_pois"],
                            "Points of interest",
                            "📍"
                        ),
                        lg=2, md=4
                    ),
                    dbc.Col(
                        create_kpi_card(
                            "Transport Stops",
                            kpis["total_transport"],
                            "Public transport infrastructure",
                            "🚌"
                        ),
                        lg=2, md=4
                    ),
                    dbc.Col(
                        create_kpi_card(
                            "Top District",
                            kpis["best_district"],
                            "Highest accessibility score",
                            "🏆"
                        ),
                        lg=4, md=8
                    ),
                ],
                className="g-4 mb-4"
            ),

            # control panel + map
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Controls", className="fw-bold mb-4", style={"color": "#0f172a"}),

                                    # 📊 ANALYSIS
                                    html.Div([
                                        html.Div("📊 Analysis", className="fw-semibold mb-2", style={"color": "#334155"}),
                                        
                                        html.Label("Metric", className="small mb-1", style={"color": "#64748b"}),
                                        dcc.Dropdown(
                                            id="metric-dropdown",
                                            options=metric_options,
                                            value=default_metric,
                                            clearable=False,
                                            className="mb-3"
                                        ),
                                    ], className="mb-4"),

                                    # ⚖ COMPARISON
                                    html.Div([
                                        html.Div("⚖ Comparison", className="fw-semibold mb-2", style={"color": "#334155"}),

                                        html.Label("District A", className="small mb-1", style={"color": "#64748b"}),
                                        dcc.Dropdown(
                                            id="district-a-dropdown",
                                            options=district_options,
                                            placeholder="Select district",
                                            className="mb-3"
                                        ),

                                        html.Label("District B", className="small mb-1", style={"color": "#64748b"}),
                                        dcc.Dropdown(
                                            id="district-b-dropdown",
                                            options=district_options,
                                            placeholder="Select district",
                                            className="mb-3"
                                        ),
                                    ], className="mb-4"),

                                    # 🔁 ACTIONS
                                    html.Div([
                                        html.Div("🔁 Actions", className="fw-semibold mb-2", style={"color": "#334155"}),

                                        dbc.Button(
                                            "Reset selection",
                                            id="reset-district-btn",
                                            color="secondary",
                                            outline=True,
                                            className="w-100"
                                        ),
                                    ], className="mb-4"),

                                    # legend
                                    html.Div([
                                        html.Div("Map Legend", className="fw-semibold mb-2", style={"color": "#334155"}),

                                        html.Div([
                                            html.Span(
                                                "Selected",
                                                className="me-2 px-2 py-1",
                                                style={
                                                    "backgroundColor": "#ef4444",
                                                    "color": "white",
                                                    "borderRadius": "6px",
                                                    "fontSize": "12px",
                                                    "fontWeight": "500"
                                                }
                                            ),
                                            html.Span(
                                                "Compare A",
                                                className="me-2 px-2 py-1",
                                                style={
                                                    "backgroundColor": "#2563eb",
                                                    "color": "white",
                                                    "borderRadius": "6px",
                                                    "fontSize": "12px",
                                                    "fontWeight": "500"
                                                }
                                            ),
                                            html.Span(
                                                "Compare B",
                                                className="me-2 px-2 py-1",
                                                style={
                                                    "backgroundColor": "#f59e0b",
                                                    "color": "white",
                                                    "borderRadius": "6px",
                                                    "fontSize": "12px",
                                                    "fontWeight": "500"
                                                }
                                            )
                                        ], className="d-flex align-items-center flex-wrap")
                                    ],
                                    className="mt-4 small")
                                ],
                                className="p-4"
                            ),
                            className="shadow-sm border-0 rounded-4 h-100"
                        ),
                        lg=3
                    ),

                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5(
                                        "District Accessibility Map", 
                                        className="fw-bold mb-3",
                                        style={"color": "#0f172a"}
                                    ),

                                    html.Div(
                                        dcc.Loading(
                                            dcc.Graph(
                                                id="district-map",
                                                figure=go.Figure().update_layout(
                                                    xaxis={"visible": False},
                                                    yaxis={"visible": False},
                                                    paper_bgcolor="rgba(0,0,0,0)",
                                                    plot_bgcolor="rgba(0,0,0,0)"
                                                ),
                                                config={"displayModeBar": False},
                                            ),
                                            type="circle",
                                            overlay_style={
                                                "visibility": "visible",
                                                "opacity": 0.4,
                                                "backgroundColor": "white"
                                            }
                                        ),
                                    )
                                ],
                                className="p-4"
                            ),
                            className="shadow-sm border-0 rounded-4 h-100"
                        ),
                        lg=9
                    ),
                ],
                className="g-4 mb-4"
            ),

            # ranking + distribution + insights
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                dbc.Tabs([
                                    # TAB 1
                                    dbc.Tab(
                                        label="📊 Top Districts Ranking",
                                        tab_id="tab-ranking",
                                        tab_style={
                                            "border": "1px solid #e2e8f0",
                                            "borderRadius": "10px 10px 0 0",
                                            "backgroundColor": "#ffffff",
                                            "marginRight": "6px"
                                        },
                                        label_style={
                                            "color": "#0f172a",
                                            "fontWeight": "600"
                                        },
                                        active_label_style={
                                            "color": "#0f172a",
                                            "fontWeight": "600"
                                        },
                                        active_tab_style={
                                            "backgroundColor": "#f8fafc",
                                            "border": "1px solid #cbd5f5",
                                        },
                                        children=[
                                            dcc.Graph(id="ranking-chart", config={"displayModeBar": False}, className="pt-3")
                                        ]
                                    ),
                                    # TAB 2
                                    dbc.Tab(
                                        label="📈 Metric Distribution",
                                        tab_id="tab-distribution",
                                        tab_style={
                                            "border": "1px solid #e2e8f0",
                                            "borderRadius": "10px 10px 0 0",
                                            "backgroundColor": "#ffffff",
                                            "marginRight": "6px"
                                        },
                                        label_style={
                                            "color": "#0f172a",
                                            "fontWeight": "600"
                                        },
                                        active_label_style={
                                            "color": "#0f172a",
                                            "fontWeight": "600"
                                        },
                                        active_tab_style={
                                            "backgroundColor": "#f8fafc",
                                            "border": "1px solid #cbd5f5",
                                        },
                                        children=[
                                            dcc.Graph(id="distribution-chart", config={"displayModeBar": False}, className="pt-3")
                                        ]
                                    ),
                                    # TAB 3
                                    dbc.Tab(
                                        label="🧠 District Insights",
                                        tab_id="tab-insights",
                                        tab_style={
                                            "border": "1px solid #e2e8f0",
                                            "borderRadius": "10px 10px 0 0",
                                            "backgroundColor": "#ffffff",
                                            "marginRight": "6px"
                                        },
                                        label_style={
                                            "color": "#0f172a",
                                            "fontWeight": "600"
                                        },
                                        active_label_style={
                                            "color": "#0f172a",
                                            "fontWeight": "600"
                                        },
                                        active_tab_style={
                                            "backgroundColor": "#f8fafc",
                                            "border": "1px solid #cbd5f5",
                                        },
                                        children=[
                                            html.Div(id="district-summary-card", className="pt-3")
                                        ]
                                    ),
                                ],
                                id="analytics-tabs",
                                active_tab="tab-ranking",
                                style={
                                    "borderBottom": "none",
                                },
                                className="mb-2"
                                )

                            ], className="p-4"),
                            className="shadow-sm border-0 rounded-4 h-100"
                        ),
                        lg=6
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5(
                                        "District Comparison", 
                                        className="fw-bold mb-3",
                                        style={"color": "#0f172a"}
                                    ),
                                    html.Div(id="district-comparison-panel")
                                ],
                                className="p-4"
                            ),
                            className="shadow-sm border-0 rounded-4 h-100"
                        ),
                        lg=6
                    )
                ],
                className="g-4 mb-4"
            ),

            # advice panel
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5(
                                        "POI Categories",
                                        className="fw-bold mb-3",
                                        style={"color": "#0f172a"}
                                    ),

                                    html.Div(
                                        id="category-cards",
                                        className="pb-2"
                                    ),

                                    dbc.Button(
                                        "Clear selection",
                                        id="reset-category-btn",
                                        color="secondary",
                                        outline=True,
                                        className="mt-2 w-100",
                                        style={"display": "none"}
                                    )
                                ],
                                className="p-4"
                            ),
                            className="shadow-sm border-0 rounded-4 h-100"
                        ),
                        lg=3
                    ),

                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5(
                                        "Recommended Locations Map",
                                        className="fw-bold mb-3",
                                        style={"color": "#0f172a"}
                                    ),
                                    dcc.Loading(
                                        html.Div(
                                            id="advice-container"
                                        ),
                                        type="circle", 
                                        overlay_style={
                                            "visibility": "visible",
                                            "opacity": 0.4,
                                            "backgroundColor": "white"
                                        }
                                    )
                                ],
                                className="p-4"
                            ),
                            className="shadow-sm border-0 rounded-4 h-100"
                        ),
                        lg=9
                    )
                ],
                className="g-4 mb-5"
            )
        ],
        fluid=True,
        className="px-4 py-4",
        style={"backgroundColor": "#f8fafc", "minHeight": "100vh"}
    )