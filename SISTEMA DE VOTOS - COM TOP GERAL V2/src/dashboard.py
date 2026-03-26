"""
Dashboard Dash — ponto de entrada para app.py em produção.

Para uso local ou em deploy (Heroku, Render, Railway):
    gunicorn app:server
"""

import json
from pathlib import Path

import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go

from .data_processor import DataProcessor
from .analytics import ElectoralAnalytics
from .visualizations import ElectoralVisualizations


def create_dashboard(data_dir: str = ".") -> dash.Dash:
    """Cria e retorna o aplicativo Dash."""

    # ── Carregar dados ─────────────────────────────────────────────
    processor = DataProcessor(data_dir)
    processor.load_data()
    df        = processor.get_combined_data()
    stats     = processor.get_summary_stats()

    analytics = ElectoralAnalytics(df)
    viz       = ElectoralVisualizations(df)

    anos   = stats["anos"]
    cargos = stats["cargos"]
    ano_default = max(anos)

    # ── Layout ─────────────────────────────────────────────────────
    app = dash.Dash(
        __name__,
        title="Dashboard Eleitoral — Rondônia",
        suppress_callback_exceptions=True,
    )

    app.layout = html.Div(
        style={"fontFamily": "Inter, sans-serif", "background": "#f5f7fa", "minHeight": "100vh"},
        children=[
            # Header
            html.Div(
                style={
                    "background": "linear-gradient(135deg,#667eea,#764ba2)",
                    "padding": "24px 40px",
                    "color": "white",
                    "marginBottom": "24px",
                },
                children=[
                    html.H1("🗳️ Sistema de Análise Eleitoral — Rondônia",
                            style={"margin": 0, "fontSize": "1.8rem"}),
                    html.P("Dados eleitorais 2016–2024 • TSE",
                           style={"margin": "6px 0 0", "opacity": 0.85}),
                ],
            ),

            # Filtros
            html.Div(
                style={"padding": "0 40px 24px"},
                children=[
                    html.Label("Ano:", style={"fontWeight": 600, "marginRight": 8}),
                    dcc.Dropdown(
                        id="filter-ano",
                        options=[{"label": str(a), "value": a} for a in anos],
                        value=ano_default,
                        clearable=False,
                        style={"width": 140, "display": "inline-block", "marginRight": 24},
                    ),
                    html.Label("Cargo:", style={"fontWeight": 600, "marginRight": 8}),
                    dcc.Dropdown(
                        id="filter-cargo",
                        options=[{"label": "Todos", "value": ""}]
                        + [{"label": c, "value": c} for c in cargos],
                        value="",
                        clearable=False,
                        style={"width": 200, "display": "inline-block"},
                    ),
                ],
            ),

            # Cards de estatísticas
            html.Div(id="stats-cards", style={"padding": "0 40px 24px"}),

            # Gráficos
            html.Div(
                style={"padding": "0 40px", "display": "grid",
                       "gridTemplateColumns": "1fr 1fr", "gap": 24},
                children=[
                    html.Div([
                        html.H3("Votos por Partido (Top 15)"),
                        dcc.Graph(id="graph-partidos"),
                    ], style={"background": "white", "borderRadius": 16,
                               "padding": 20, "boxShadow": "0 4px 20px rgba(0,0,0,0.08)"}),
                    html.Div([
                        html.H3("Votos por Município (Top 20)"),
                        dcc.Graph(id="graph-municipios"),
                    ], style={"background": "white", "borderRadius": 16,
                               "padding": 20, "boxShadow": "0 4px 20px rgba(0,0,0,0.08)"}),
                    html.Div([
                        html.H3("Evolução de Votos por Ano"),
                        dcc.Graph(id="graph-temporal",
                                  figure=viz.plot_temporal_overview()),
                    ], style={"background": "white", "borderRadius": 16,
                               "padding": 20, "boxShadow": "0 4px 20px rgba(0,0,0,0.08)"}),
                    html.Div([
                        html.H3("Votos por Cargo e Partido"),
                        dcc.Graph(id="graph-cargo-partido"),
                    ], style={"background": "white", "borderRadius": 16,
                               "padding": 20, "boxShadow": "0 4px 20px rgba(0,0,0,0.08)"}),
                ],
            ),

            # Tabela top candidatos
            html.Div(
                style={"padding": "24px 40px"},
                children=[
                    html.Div(
                        style={"background": "white", "borderRadius": 16,
                               "padding": 20, "boxShadow": "0 4px 20px rgba(0,0,0,0.08)"},
                        children=[
                            html.H3("Top 20 Candidatos"),
                            html.Div(id="table-candidatos"),
                        ],
                    )
                ],
            ),

            html.Footer(
                "Sistema de Análise Eleitoral • Rondônia • Dados: TSE",
                style={"textAlign": "center", "padding": "24px", "color": "#888"},
            ),
        ],
    )

    # ── Callbacks ──────────────────────────────────────────────────

    @app.callback(
        Output("stats-cards",        "children"),
        Output("graph-partidos",     "figure"),
        Output("graph-municipios",   "figure"),
        Output("graph-cargo-partido","figure"),
        Output("table-candidatos",   "children"),
        Input("filter-ano",   "value"),
        Input("filter-cargo", "value"),
    )
    def update_all(ano_val, cargo_val):
        _ano   = int(ano_val) if ano_val else None
        _cargo = cargo_val or None

        _df = df.copy()
        if _ano:
            _df = _df[_df["ANO"] == _ano]
        if _cargo:
            _df = _df[_df["CARGO"] == _cargo]

        # Stats
        total_votos      = int(_df["VOTOS"].sum())
        total_candidatos = int(_df["CANDIDATO"].nunique())
        total_partidos   = int(_df["PARTIDO"].nunique())
        total_municipios = int(_df["MUNICÍPIO"].nunique())

        card_style = {
            "background": "white", "borderRadius": 16, "padding": "20px 28px",
            "boxShadow": "0 4px 20px rgba(0,0,0,0.08)", "textAlign": "center",
        }
        cards = html.Div(
            style={"display": "grid",
                   "gridTemplateColumns": "repeat(4, 1fr)", "gap": 16},
            children=[
                html.Div([html.Div("🗳️", style={"fontSize": "2rem"}),
                          html.Div(f"{total_votos:,}", style={"fontSize": "1.8rem", "fontWeight": 700, "color": "#3498DB"}),
                          html.Div("Total de Votos", style={"color": "#888"})], style=card_style),
                html.Div([html.Div("👥", style={"fontSize": "2rem"}),
                          html.Div(f"{total_candidatos:,}", style={"fontSize": "1.8rem", "fontWeight": 700, "color": "#27AE60"}),
                          html.Div("Candidatos", style={"color": "#888"})], style=card_style),
                html.Div([html.Div("🏛️", style={"fontSize": "2rem"}),
                          html.Div(f"{total_partidos}", style={"fontSize": "1.8rem", "fontWeight": 700, "color": "#F39C12"}),
                          html.Div("Partidos", style={"color": "#888"})], style=card_style),
                html.Div([html.Div("🏙️", style={"fontSize": "2rem"}),
                          html.Div(f"{total_municipios}", style={"fontSize": "1.8rem", "fontWeight": 700, "color": "#9B59B6"}),
                          html.Div("Municípios", style={"color": "#888"})], style=card_style),
            ],
        )

        _viz = ElectoralVisualizations(_df)
        fig_partidos  = _viz.plot_votes_by_party()
        fig_munis     = _viz.plot_geographic_heatmap()
        fig_cargos    = _viz.plot_elected_by_party()

        # Top candidatos
        top = (
            _df.groupby(["CANDIDATO", "PARTIDO", "CARGO"])
            .agg(TOTAL_VOTOS=("VOTOS", "sum"))
            .reset_index()
            .sort_values("TOTAL_VOTOS", ascending=False)
            .head(20)
        )
        rows = [
            html.Tr([html.Th("#"), html.Th("Candidato"), html.Th("Partido"),
                     html.Th("Cargo"), html.Th("Votos")],
                    style={"background": "#f8f9fa"})
        ]
        for i, (_, r) in enumerate(top.iterrows()):
            rows.append(html.Tr([
                html.Td(i + 1),
                html.Td(html.Strong(r["CANDIDATO"])),
                html.Td(r["PARTIDO"]),
                html.Td(r["CARGO"]),
                html.Td(f"{int(r['TOTAL_VOTOS']):,}", style={"fontWeight": 700}),
            ]))

        table = html.Table(
            rows,
            style={"width": "100%", "borderCollapse": "collapse",
                   "fontSize": "0.9rem"},
        )

        return cards, fig_partidos, fig_munis, fig_cargos, table

    return app
