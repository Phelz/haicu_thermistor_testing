# # # import dash

# # # def create_layout(App: dash.Dash, server=None) -> dash.html.Div:
# # #     return dash.html.Div(
# # #         [
            
            
            
            
            
# # #         ]
# # #     )


# # """
# # layouts/home_layout.py
# # Home page layout: interactive Plotly time-series for all 16 thermistor channels.
# # Refreshes automatically every hour via a dcc.Interval.
# # """

# # import dash
# # from dash import dcc, html, Input, Output, callback
# # import plotly.graph_objects as go
# # import data_parser  # adjust import path if needed


# # # ── Colour palette: 16 distinct colours ──────────────────────────────────────
# # CHANNEL_COLORS = [
# #     "#e63946", "#f4a261", "#2a9d8f", "#457b9d",
# #     "#a8dadc", "#f1faee", "#6a4c93", "#1982c4",
# #     "#8ac926", "#ff595e", "#ffca3a", "#6a994e",
# #     "#bc6c25", "#cdb4db", "#ffc8dd", "#a2d2ff",
# # ]


# # def build_figure(df) -> go.Figure:
# #     fig = go.Figure()

# #     for ch in sorted(df["channel"].unique()):
# #         sub = df[df["channel"] == ch].sort_values("timestamp")
# #         fig.add_trace(go.Scatter(
# #             x=sub["timestamp"],
# #             y=sub["value"],
# #             mode="lines",
# #             name=f"Ch {ch:02d}",
# #             line=dict(color=CHANNEL_COLORS[ch % len(CHANNEL_COLORS)], width=1.5),
# #             hovertemplate="<b>Ch %d</b><br>%%{x|%%H:%%M:%%S}<br>Value: %%{y}<extra></extra>" % ch,
# #         ))

# #     fig.update_layout(
# #         template="plotly_dark",
# #         paper_bgcolor="#0d1117",
# #         plot_bgcolor="#0d1117",
# #         font=dict(family="'IBM Plex Mono', monospace", color="#c9d1d9", size=12),
# #         title=dict(
# #             text="Thermistor Channels — Raw ADC Values",
# #             font=dict(size=18, color="#e6edf3"),
# #             x=0.01,
# #         ),
# #         legend=dict(
# #             bgcolor="rgba(22,27,34,0.8)",
# #             bordercolor="#30363d",
# #             borderwidth=1,
# #             font=dict(size=11),
# #             tracegroupgap=2,
# #         ),
# #         xaxis=dict(
# #             title="Time",
# #             gridcolor="#21262d",
# #             linecolor="#30363d",
# #             tickformat="%H:%M",
# #             rangeslider=dict(visible=True, bgcolor="#161b22", thickness=0.06),
# #         ),
# #         yaxis=dict(
# #             title="ADC Value (0 – 1023)",
# #             gridcolor="#21262d",
# #             linecolor="#30363d",
# #             range=[-20, 1043],
# #         ),
# #         hovermode="x unified",
# #         margin=dict(l=60, r=20, t=60, b=60),
# #     )
# #     return fig


# # def create_layout(App: dash.Dash, server=None) -> html.Div:

# #     # ── Register the refresh callback once ───────────────────────────────────
# #     @callback(
# #         Output("thermistor-graph", "figure"),
# #         Input("hourly-interval", "n_intervals"),
# #     )
# #     def refresh_graph(_n):
# #         df = data_parser.parse_data()
# #         return build_figure(df)

# #     # ── Initial load ─────────────────────────────────────────────────────────
# #     try:
# #         initial_df = data_parser.parse_data()
# #         initial_fig = build_figure(initial_df)
# #     except Exception:
# #         initial_fig = go.Figure()

# #     # ── Layout ───────────────────────────────────────────────────────────────
# #     return html.Div(
# #         style={
# #             "minHeight": "100vh",
# #             "backgroundColor": "#0d1117",
# #             "fontFamily": "'IBM Plex Mono', monospace",
# #             "padding": "24px 32px",
# #         },
# #         children=[
# #             # Header
# #             html.Div(
# #                 style={"marginBottom": "24px", "borderBottom": "1px solid #21262d", "paddingBottom": "16px"},
# #                 children=[
# #                     html.H1(
# #                         "HAICU Thermistor Testing",
# #                         style={"color": "#e6edf3", "fontSize": "1.6rem", "margin": 0, "letterSpacing": "0.04em"},
# #                     ),
# #                     html.P(
# #                         "Live ADC readings · 16 channels · 10 s resolution · auto-refresh every hour",
# #                         style={"color": "#8b949e", "fontSize": "0.8rem", "margin": "6px 0 0 0"},
# #                     ),
# #                 ],
# #             ),

# #             # Graph
# #             dcc.Graph(
# #                 id="thermistor-graph",
# #                 figure=initial_fig,
# #                 style={"height": "70vh"},
# #                 config={
# #                     "displayModeBar": True,
# #                     "modeBarButtonsToRemove": ["select2d", "lasso2d"],
# #                     "toImageButtonOptions": {"format": "png", "filename": "thermistor_data"},
# #                 },
# #             ),

# #             # Hourly refresh interval  (3 600 000 ms = 1 hour)
# #             dcc.Interval(
# #                 id="hourly-interval",
# #                 interval=3_600_000,
# #                 n_intervals=0,
# #             ),
# #         ],
# #     )


# """
# layouts/home_layout.py
# Home page layout: interactive Plotly time-series for all 16 thermistor channels.
#   - Reads all data from data/<YYYY-MM-DD>/<HH>.txt
#   - Downsampling selector: None (10 s) / 1 min / 5 min / 10 min
#   - Auto-refreshes every hour via dcc.Interval
# """

# import dash
# from dash import dcc, html, Input, Output, callback
# import plotly.graph_objects as go
# import data_parser
# from data_parser import RESAMPLE_OPTIONS


# # ── 16 distinct channel colours ───────────────────────────────────────────────
# CHANNEL_COLORS = [
#     "#e63946", "#f4a261", "#2a9d8f", "#457b9d",
#     "#a8dadc", "#c8f1e9", "#6a4c93", "#1982c4",
#     "#8ac926", "#ff595e", "#ffca3a", "#6a994e",
#     "#bc6c25", "#cdb4db", "#ffc8dd", "#a2d2ff",
# ]


# def build_figure(df) -> go.Figure:
#     fig = go.Figure()

#     if df.empty:
#         fig.update_layout(
#             template="plotly_dark",
#             paper_bgcolor="#0d1117",
#             plot_bgcolor="#0d1117",
#             annotations=[dict(
#                 text="No data found — check your data/ directory.",
#                 x=0.5, y=0.5, xref="paper", yref="paper",
#                 showarrow=False, font=dict(color="#8b949e", size=14),
#             )],
#         )
#         return fig

#     for ch in sorted(df["channel"].unique()):
#         sub = df[df["channel"] == ch].sort_values("timestamp")
#         fig.add_trace(go.Scatter(
#             x=sub["timestamp"],
#             y=sub["value"],
#             mode="lines",
#             name=f"Ch {ch:02d}",
#             line=dict(color=CHANNEL_COLORS[ch % len(CHANNEL_COLORS)], width=1.5),
#             hovertemplate=(
#                 f"<b>Ch {ch:02d}</b><br>"
#                 "%{x|%Y-%m-%d %H:%M:%S}<br>"
#                 "Value: %{y}<extra></extra>"
#             ),
#         ))

#     # x-axis tick format depends on span of data
#     ts_min = df["timestamp"].min()
#     ts_max = df["timestamp"].max()
#     span_days = (ts_max - ts_min).total_seconds() / 86400
#     tick_fmt = "%b %d %H:%M" if span_days > 1 else "%H:%M:%S"

#     fig.update_layout(
#         template="plotly_dark",
#         paper_bgcolor="#0d1117",
#         plot_bgcolor="#0d1117",
#         font=dict(family="'IBM Plex Mono', monospace", color="#c9d1d9", size=12),
#         title=dict(
#             text="Thermistor Channels — Raw ADC Values",
#             font=dict(size=18, color="#e6edf3"),
#             x=0.01,
#         ),
#         legend=dict(
#             bgcolor="rgba(22,27,34,0.85)",
#             bordercolor="#30363d",
#             borderwidth=1,
#             font=dict(size=11),
#             tracegroupgap=2,
#         ),
#         xaxis=dict(
#             title="Time",
#             gridcolor="#21262d",
#             linecolor="#30363d",
#             tickformat=tick_fmt,
#             rangeslider=dict(visible=True, bgcolor="#161b22", thickness=0.06),
#         ),
#         yaxis=dict(
#             title="ADC Value (0 – 1023)",
#             gridcolor="#21262d",
#             linecolor="#30363d",
#             range=[-20, 1043],
#         ),
#         hovermode="x unified",
#         margin=dict(l=60, r=20, t=60, b=60),
#     )
#     return fig


# def create_layout(App: dash.Dash, server=None) -> html.Div:

#     # ── Callback: rebuild figure on interval tick OR downsample change ────────
#     @callback(
#         Output("thermistor-graph", "figure"),
#         Output("data-info", "children"),
#         Input("hourly-interval", "n_intervals"),
#         Input("downsample-select", "value"),
#     )
#     def refresh_graph(_n, resample_label):
#         df_raw = data_parser.parse_all()
#         rule = RESAMPLE_OPTIONS.get(resample_label)
#         df = data_parser.downsample(df_raw, rule)

#         if df_raw.empty:
#             info = "No data loaded."
#         else:
#             days = df_raw["timestamp"].dt.date.nunique()
#             pts = len(df_raw) // 16  # timestamps
#             pts_ds = len(df) // 16
#             info = (
#                 f"{days} day{'s' if days != 1 else ''} · "
#                 f"{pts:,} raw timestamps · "
#                 f"{pts_ds:,} displayed"
#             )

#         return build_figure(df), info

#     # ── Initial load ──────────────────────────────────────────────────────────
#     try:
#         df_raw = data_parser.parse_all()
#         df_init = data_parser.downsample(df_raw, None)
#         initial_fig = build_figure(df_init)
#         days = df_raw["timestamp"].dt.date.nunique() if not df_raw.empty else 0
#         pts = len(df_raw) // 16 if not df_raw.empty else 0
#         initial_info = (
#             f"{days} day{'s' if days != 1 else ''} · {pts:,} raw timestamps · {pts:,} displayed"
#             if not df_raw.empty else "No data loaded."
#         )
#     except Exception as e:
#         initial_fig = go.Figure()
#         initial_info = f"Error loading data: {e}"

#     # ── Layout ────────────────────────────────────────────────────────────────
#     return html.Div(
#         style={
#             "minHeight": "100vh",
#             "backgroundColor": "#0d1117",
#             "fontFamily": "'IBM Plex Mono', monospace",
#             "padding": "24px 32px",
#         },
#         children=[

#             # Header
#             html.Div(
#                 style={
#                     "display": "flex",
#                     "alignItems": "flex-end",
#                     "justifyContent": "space-between",
#                     "borderBottom": "1px solid #21262d",
#                     "paddingBottom": "16px",
#                     "marginBottom": "20px",
#                     "flexWrap": "wrap",
#                     "gap": "12px",
#                 },
#                 children=[
#                     html.Div([
#                         html.H1(
#                             "HAICU Thermistor Testing",
#                             style={
#                                 "color": "#e6edf3",
#                                 "fontSize": "1.6rem",
#                                 "margin": 0,
#                                 "letterSpacing": "0.04em",
#                             },
#                         ),
#                         html.P(
#                             id="data-info",
#                             children=initial_info,
#                             style={"color": "#8b949e", "fontSize": "0.78rem", "margin": "5px 0 0 0"},
#                         ),
#                     ]),

#                     # Downsample control
#                     html.Div(
#                         style={"display": "flex", "alignItems": "center", "gap": "10px"},
#                         children=[
#                             html.Label(
#                                 "Downsample:",
#                                 style={"color": "#8b949e", "fontSize": "0.8rem", "whiteSpace": "nowrap"},
#                             ),
#                             dcc.Dropdown(
#                                 id="downsample-select",
#                                 options=[{"label": k, "value": k} for k in RESAMPLE_OPTIONS],
#                                 value="None (10 s)",
#                                 clearable=False,
#                                 style={
#                                     "width": "140px",
#                                     "fontSize": "0.82rem",
#                                     "backgroundColor": "#161b22",
#                                     "color": "#c9d1d9",
#                                     "border": "1px solid #30363d",
#                                     "borderRadius": "6px",
#                                 },
#                             ),
#                         ],
#                     ),
#                 ],
#             ),

#             # Graph
#             dcc.Graph(
#                 id="thermistor-graph",
#                 figure=initial_fig,
#                 style={"height": "72vh"},
#                 config={
#                     "displayModeBar": True,
#                     "modeBarButtonsToRemove": ["select2d", "lasso2d"],
#                     "toImageButtonOptions": {
#                         "format": "png",
#                         "filename": "thermistor_data",
#                         "scale": 2,
#                     },
#                 },
#             ),

#             # Hourly refresh interval (3 600 000 ms = 1 h)
#             dcc.Interval(
#                 id="hourly-interval",
#                 interval=3_600_000,
#                 n_intervals=0,
#             ),
#         ],
#     )


"""
layouts/home_layout.py
Home page layout: interactive Plotly time-series for all 16 thermistor channels.
  - Reads all data from data/<YYYY-MM-DD>/<HH>.txt
  - Toggle between Raw ADC and °C
  - Downsampling selector: None (10 s) / 1 min / 5 min / 10 min
  - Auto-refreshes every hour via dcc.Interval
"""

import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import data_parser
from data_parser import RESAMPLE_OPTIONS


# ── 16 distinct channel colours ───────────────────────────────────────────────
CHANNEL_COLORS = [
    "#e63946", "#f4a261", "#2a9d8f", "#457b9d",
    "#a8dadc", "#c8f1e9", "#6a4c93", "#1982c4",
    "#8ac926", "#ff595e", "#ffca3a", "#6a994e",
    "#bc6c25", "#cdb4db", "#ffc8dd", "#a2d2ff",
]

# ── Shared style tokens ───────────────────────────────────────────────────────
BG        = "#0d1117"
SURFACE   = "#161b22"
BORDER    = "#30363d"
TEXT      = "#e6edf3"
MUTED     = "#8b949e"
FONT      = "'IBM Plex Mono', monospace"

TOGGLE_BASE = {
    "padding": "5px 14px",
    "border": f"1px solid {BORDER}",
    "borderRadius": "6px",
    "fontSize": "0.8rem",
    "cursor": "pointer",
    "fontFamily": FONT,
    "transition": "background 0.15s, color 0.15s",
}
TOGGLE_ACTIVE   = {**TOGGLE_BASE, "backgroundColor": "#238636", "color": "#fff",   "borderColor": "#238636"}
TOGGLE_INACTIVE = {**TOGGLE_BASE, "backgroundColor": SURFACE,   "color": MUTED,    "borderColor": BORDER}


def build_figure(df, mode: str) -> go.Figure:
    """
    mode: 'raw' → plot raw ADC values
          'celsius' → plot °C values
    """
    fig = go.Figure()

    if df.empty:
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor=BG, plot_bgcolor=BG,
            annotations=[dict(
                text="No data found — check your data/ directory.",
                x=0.5, y=0.5, xref="paper", yref="paper",
                showarrow=False, font=dict(color=MUTED, size=14),
            )],
        )
        return fig

    use_celsius = (mode == "celsius")
    y_col   = "celsius" if use_celsius else "raw"
    y_label = "Temperature (°C)" if use_celsius else "ADC Value (0 – 1023)"
    y_range = None if use_celsius else [-20, 1043]

    for ch in sorted(df["channel"].unique()):
        sub = df[df["channel"] == ch].sort_values("timestamp")
        y   = sub[y_col]

        # Skip channel if all celsius values are NaN
        if use_celsius and y.isna().all():
            continue

        fig.add_trace(go.Scatter(
            x=sub["timestamp"],
            y=y,
            mode="lines",
            name=f"Ch {ch:02d}",
            line=dict(color=CHANNEL_COLORS[ch % len(CHANNEL_COLORS)], width=1.5),
            connectgaps=False,  # leave gaps where conversion returned None
            hovertemplate=(
                f"<b>Ch {ch:02d}</b><br>"
                "%{x|%Y-%m-%d %H:%M:%S}<br>"
                + ("Temp: %{y:.2f} °C" if use_celsius else "ADC: %{y}")
                + "<extra></extra>"
            ),
        ))

    ts_min = df["timestamp"].min()
    ts_max = df["timestamp"].max()
    span_days = (ts_max - ts_min).total_seconds() / 86400 if pd.notna(ts_min) else 0
    tick_fmt = "%b %d %H:%M" if span_days > 1 else "%H:%M:%S"

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font=dict(family=FONT, color="#c9d1d9", size=12),
        title=dict(
            text="Thermistor Channels — " + ("Temperature (°C)" if use_celsius else "Raw ADC Values"),
            font=dict(size=18, color=TEXT),
            x=0.01,
        ),
        legend=dict(
            bgcolor="rgba(22,27,34,0.85)",
            bordercolor=BORDER,
            borderwidth=1,
            font=dict(size=11),
            tracegroupgap=2,
        ),
        xaxis=dict(
            title="Time",
            gridcolor="#21262d",
            linecolor=BORDER,
            tickformat=tick_fmt,
            rangeslider=dict(visible=True, bgcolor=SURFACE, thickness=0.06),
        ),
        yaxis=dict(
            title=y_label,
            gridcolor="#21262d",
            linecolor=BORDER,
            **({"range": y_range} if y_range else {}),
        ),
        hovermode="x unified",
        margin=dict(l=60, r=20, t=60, b=60),
    )
    return fig


import pandas as pd  # needed for pd.notna above


def create_layout(App: dash.Dash, server=None) -> html.Div:

    # ── Callbacks ─────────────────────────────────────────────────────────────

    @callback(
        Output("thermistor-graph", "figure"),
        Output("data-info", "children"),
        Input("hourly-interval", "n_intervals"),
        Input("downsample-select", "value"),
        Input("mode-store", "data"),
    )
    def refresh_graph(_n, resample_label, mode):
        df_raw = data_parser.parse_all()
        rule   = RESAMPLE_OPTIONS.get(resample_label)
        df     = data_parser.downsample(df_raw, rule)
        mode   = mode or "raw"

        if df_raw.empty:
            info = "No data loaded."
        else:
            days   = df_raw["timestamp"].dt.date.nunique()
            pts    = len(df_raw) // 16
            pts_ds = len(df) // 16
            info   = (
                f"{days} day{'s' if days != 1 else ''} · "
                f"{pts:,} raw timestamps · "
                f"{pts_ds:,} displayed"
            )

        return build_figure(df, mode), info

    @callback(
        Output("mode-store", "data"),
        Output("btn-raw", "style"),
        Output("btn-celsius", "style"),
        Input("btn-raw", "n_clicks"),
        Input("btn-celsius", "n_clicks"),
    )
    def toggle_mode(n_raw, n_cel):
        ctx = dash.callback_context
        if not ctx.triggered or ctx.triggered[0]["prop_id"].startswith("btn-raw"):
            return "raw", TOGGLE_ACTIVE, TOGGLE_INACTIVE
        return "celsius", TOGGLE_INACTIVE, TOGGLE_ACTIVE

    # ── Initial load ──────────────────────────────────────────────────────────
    try:
        df_raw0  = data_parser.parse_all()
        df_init  = data_parser.downsample(df_raw0, None)
        init_fig = build_figure(df_init, "raw")
        days0    = df_raw0["timestamp"].dt.date.nunique() if not df_raw0.empty else 0
        pts0     = len(df_raw0) // 16 if not df_raw0.empty else 0
        init_info = (
            f"{days0} day{'s' if days0 != 1 else ''} · {pts0:,} raw timestamps · {pts0:,} displayed"
            if not df_raw0.empty else "No data loaded."
        )
    except Exception as e:
        init_fig  = go.Figure()
        init_info = f"Error loading data: {e}"

    # ── Layout ────────────────────────────────────────────────────────────────
    return html.Div(
        style={"minHeight": "100vh", "backgroundColor": BG, "fontFamily": FONT, "padding": "24px 32px"},
        children=[

            # Header row
            html.Div(
                style={
                    "display": "flex", "alignItems": "flex-end",
                    "justifyContent": "space-between",
                    "borderBottom": f"1px solid {BORDER}",
                    "paddingBottom": "16px", "marginBottom": "20px",
                    "flexWrap": "wrap", "gap": "12px",
                },
                children=[
                    # Title + info
                    html.Div([
                        html.H1("HAICU Thermistor Testing", style={
                            "color": TEXT, "fontSize": "1.6rem", "margin": 0, "letterSpacing": "0.04em",
                        }),
                        html.P(id="data-info", children=init_info, style={
                            "color": MUTED, "fontSize": "0.78rem", "margin": "5px 0 0 0",
                        }),
                    ]),

                    # Controls row
                    html.Div(
                        style={"display": "flex", "alignItems": "center", "gap": "20px", "flexWrap": "wrap"},
                        children=[

                            # Raw / °C toggle
                            html.Div(
                                style={"display": "flex", "alignItems": "center", "gap": "8px"},
                                children=[
                                    html.Label("Display:", style={"color": MUTED, "fontSize": "0.8rem"}),
                                    html.Button("Raw ADC", id="btn-raw",     n_clicks=0, style=TOGGLE_ACTIVE),
                                    html.Button("°C",      id="btn-celsius", n_clicks=0, style=TOGGLE_INACTIVE),
                                ],
                            ),

                            # Downsample dropdown
                            html.Div(
                                style={"display": "flex", "alignItems": "center", "gap": "8px"},
                                children=[
                                    html.Label("Downsample:", style={"color": MUTED, "fontSize": "0.8rem", "whiteSpace": "nowrap"}),
                                    dcc.Dropdown(
                                        id="downsample-select",
                                        options=[{"label": k, "value": k} for k in RESAMPLE_OPTIONS],
                                        value="None (10 s)",
                                        clearable=False,
                                        style={
                                            "width": "140px", "fontSize": "0.82rem",
                                            "backgroundColor": SURFACE, "color": "#c9d1d9",
                                            "border": f"1px solid {BORDER}", "borderRadius": "6px",
                                        },
                            )],
                            ),
                        ],
                    ),
                ],
            ),

            # Graph
            dcc.Graph(
                id="thermistor-graph",
                figure=init_fig,
                style={"height": "72vh"},
                config={
                    "displayModeBar": True,
                    "modeBarButtonsToRemove": ["select2d", "lasso2d"],
                    "toImageButtonOptions": {"format": "png", "filename": "thermistor_data", "scale": 2},
                },
            ),

            # Hidden store for current display mode
            dcc.Store(id="mode-store", data="raw"),

            # Hourly refresh (3 600 000 ms = 1 h)
            dcc.Interval(id="hourly-interval", interval=3_600_000, n_intervals=0),
        ],
    )
