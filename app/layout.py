from dash import html, dcc
import dash_bootstrap_components as dbc

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
                                    html.H5(
                                        "Controls", 
                                        className="fw-bold mb-4",
                                        style={"color": "#0f172a"}
                                    ),
                                    html.Label(
                                        "Metric", 
                                        className="fw-semibold mb-2",
                                        style={"color": "#334155"}
                                    ),
                                    dcc.Dropdown(
                                        id="metric-dropdown",
                                        options=metric_options,
                                        value=default_metric,
                                        clearable=False,
                                        className="mb-4"
                                    ),

                                    html.Label(
                                        "Compare district A", 
                                        className="fw-semibold mb-2",
                                        style={"color": "#334155"}
                                    ),
                                    dcc.Dropdown(
                                        id="district-a-dropdown",
                                        options=district_options,
                                        value=district_options[0]["value"] if district_options else None,
                                        clearable=False,
                                        className="mb-4"
                                    ),

                                    html.Label(
                                        "Compare district B", 
                                        className="fw-semibold mb-2",
                                        style={"color": "#334155"}
                                    ),
                                    dcc.Dropdown(
                                        id="district-b-dropdown",
                                        options=district_options,
                                        value=district_options[1]["value"] if len(district_options) > 1 else None,
                                        clearable=False
                                    ),
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
                                    dcc.Graph(id="district-map", config={"displayModeBar": False})
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

            # secondary visuals
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5(
                                        "Top District Ranking", 
                                        className="fw-bold mb-3",
                                        style={"color": "#0f172a"}
                                    ),
                                    dcc.Graph(id="ranking-chart", config={"displayModeBar": False})
                                ],
                                className="p-4"
                            ),
                            className="shadow-sm border-0 rounded-4 h-100"
                        ),
                        lg=6
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5(
                                        "Metric Distribution", 
                                        className="fw-bold mb-3",
                                        style={"color": "#0f172a"}
                                    ),
                                    dcc.Graph(id="distribution-chart", config={"displayModeBar": False})
                                ],
                                className="p-4"
                            ),
                            className="shadow-sm border-0 rounded-4 h-100"
                        ),
                        lg=6
                    ),
                ],
                className="g-4 mb-4"
            ),

            # insights panels
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5(
                                        "District Insights", 
                                        className="fw-bold mb-3",
                                        style={"color": "#0f172a"}
                                    ),
                                    html.Div(id="district-summary-card", className="pb-2")
                                ],
                                className="p-4"
                            ),
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
                    ),
                ],
                className="g-4 mb-5"
            )
        ],
        fluid=True,
        className="px-4 py-4",
        style={"backgroundColor": "#f8fafc", "minHeight": "100vh"}
    )