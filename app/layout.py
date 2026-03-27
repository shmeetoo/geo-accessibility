from dash import html, dcc
import dash_bootstrap_components as dbc

def create_layout(metric_options, default_metric):
    return dbc.Container(
        [
            html.H1("Geo Accessibility Dashboard", className="my-4"),

            html.P(
                "Interactive dashboard for district-level geospatial analysis.",
                className="text-muted"
            ),

            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Select metric:"),
                            dcc.Dropdown(
                                id="metric-dropdown",
                                options=metric_options,
                                value=default_metric,
                                clearable=False
                            )
                        ],
                        width=4
                    )
                ],
                class_name="mb-4"
            ),

            dbc.Row(
                [
                    dbc.Col(
                        [
                            dcc.Graph(id="ranking-chart"),
                            html.Div(id="district-summary-card", className="mt-4")
                        ],
                        width=4
                    )
                ]
            )
        ],
        fluid=True
    )