"""
ElectoralVisualizations — gráficos Plotly para o relatório eleitoral.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


# Paleta de cores padrão
_COLORS = px.colors.qualitative.Plotly


class ElectoralVisualizations:
    """Cria figuras Plotly a partir do DataFrame eleitoral."""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def _filter(self, ano: int = None) -> pd.DataFrame:
        return self.df if ano is None else self.df[self.df["ANO"] == ano]

    # ── Votos por Partido ──────────────────────────────────────────

    def plot_votes_by_party(self, ano: int = None) -> go.Figure:
        """Gráfico de barras horizontais — top 15 partidos por votos."""
        df = self._filter(ano)
        data = (
            df.groupby("PARTIDO")["VOTOS"]
            .sum()
            .nlargest(15)
            .sort_values(ascending=True)
        )

        fig = go.Figure(
            go.Bar(
                x=data.values,
                y=data.index,
                orientation="h",
                marker=dict(
                    color=data.values,
                    colorscale="Viridis",
                    showscale=False,
                ),
                text=[f"{v:,.0f}" for v in data.values],
                textposition="outside",
            )
        )
        fig.update_layout(
            xaxis_title="Total de Votos",
            yaxis_title="Partido",
            margin=dict(l=10, r=60, t=10, b=40),
            plot_bgcolor="white",
            paper_bgcolor="white",
        )
        return fig

    # ── Distribuição por Município ─────────────────────────────────

    def plot_geographic_heatmap(self, ano: int = None) -> go.Figure:
        """Gráfico de barras horizontais — top 20 municípios por votos."""
        df = self._filter(ano)
        data = (
            df.groupby("MUNICÍPIO")["VOTOS"]
            .sum()
            .nlargest(20)
            .sort_values(ascending=True)
        )

        fig = go.Figure(
            go.Bar(
                x=data.values,
                y=data.index,
                orientation="h",
                marker=dict(
                    color=data.values,
                    colorscale="Blues",
                    showscale=False,
                ),
                text=[f"{v:,.0f}" for v in data.values],
                textposition="outside",
            )
        )
        fig.update_layout(
            xaxis_title="Total de Votos",
            yaxis_title="Município",
            margin=dict(l=10, r=60, t=10, b=40),
            plot_bgcolor="white",
            paper_bgcolor="white",
        )
        return fig

    # ── Eleitos por Partido e Cargo ────────────────────────────────

    def plot_elected_by_party(self, ano: int = None) -> go.Figure:
        """Gráfico de barras empilhadas — top 10 partidos × cargo."""
        df = self._filter(ano)

        top_partidos = (
            df.groupby("PARTIDO")["VOTOS"].sum().nlargest(10).index.tolist()
        )
        data = (
            df[df["PARTIDO"].isin(top_partidos)]
            .groupby(["PARTIDO", "CARGO"])["VOTOS"]
            .sum()
            .reset_index()
        )

        fig = go.Figure()
        for i, cargo in enumerate(sorted(data["CARGO"].unique())):
            sub = data[data["CARGO"] == cargo]
            vals = [
                int(sub.loc[sub["PARTIDO"] == p, "VOTOS"].sum())
                for p in top_partidos
            ]
            fig.add_trace(
                go.Bar(
                    name=cargo,
                    x=top_partidos,
                    y=vals,
                    marker_color=_COLORS[i % len(_COLORS)],
                )
            )

        fig.update_layout(
            barmode="stack",
            xaxis_title="Partido",
            yaxis_title="Total de Votos",
            legend_title="Cargo",
            margin=dict(l=10, r=10, t=10, b=80),
            plot_bgcolor="white",
            paper_bgcolor="white",
        )
        return fig

    # ── Treemap por Município ──────────────────────────────────────

    def plot_treemap_municipalities(self, ano: int = None) -> go.Figure:
        """Treemap de votos: Estado → Município → Cargo."""
        df = self._filter(ano)
        data = (
            df.groupby(["MUNICÍPIO", "CARGO"])["VOTOS"]
            .sum()
            .reset_index()
        )
        data = data[data["VOTOS"] > 0]

        ids      = ["Rondônia"]
        labels   = ["Rondônia"]
        parents  = [""]
        values   = [int(df["VOTOS"].sum())]

        # Municípios
        for muni in data["MUNICÍPIO"].unique():
            total = int(data.loc[data["MUNICÍPIO"] == muni, "VOTOS"].sum())
            ids.append(muni)
            labels.append(muni)
            parents.append("Rondônia")
            values.append(total)

        # Cargo dentro de cada município
        for _, row in data.iterrows():
            node_id = f"{row['MUNICÍPIO']} / {row['CARGO']}"
            ids.append(node_id)
            labels.append(row["CARGO"])
            parents.append(row["MUNICÍPIO"])
            values.append(int(row["VOTOS"]))

        fig = go.Figure(
            go.Treemap(
                ids=ids,
                labels=labels,
                parents=parents,
                values=values,
                branchvalues="total",
                textinfo="label+value+percent parent",
                marker=dict(colorscale="Purples"),
            )
        )
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        return fig

    # ── Sunburst ───────────────────────────────────────────────────

    def plot_sunburst_results(self, ano: int = None) -> go.Figure:
        """Sunburst: Cargo → Partido → total de votos."""
        df = self._filter(ano)

        cargo_data = (
            df.groupby("CARGO")["VOTOS"].sum().reset_index()
        )
        pc_data = (
            df.groupby(["CARGO", "PARTIDO"])["VOTOS"]
            .sum()
            .reset_index()
        )
        pc_data = pc_data[pc_data["VOTOS"] > 0]

        labels  = list(cargo_data["CARGO"])
        parents = [""] * len(cargo_data)
        values  = list(cargo_data["VOTOS"].astype(int))

        for _, row in pc_data.iterrows():
            labels.append(f"{row['PARTIDO']} ({row['CARGO']})")
            parents.append(row["CARGO"])
            values.append(int(row["VOTOS"]))

        fig = go.Figure(
            go.Sunburst(
                labels=labels,
                parents=parents,
                values=values,
                branchvalues="total",
                textinfo="label+percent parent",
                insidetextorientation="radial",
            )
        )
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        return fig

    # ── Panorama Temporal ──────────────────────────────────────────

    def plot_temporal_overview(self) -> go.Figure:
        """Linhas de evolução de votos por cargo ao longo dos anos."""
        data = (
            self.df.groupby(["ANO", "CARGO"])["VOTOS"]
            .sum()
            .reset_index()
            .sort_values("ANO")
        )

        fig = go.Figure()
        for i, cargo in enumerate(sorted(data["CARGO"].unique())):
            sub = data[data["CARGO"] == cargo]
            fig.add_trace(
                go.Scatter(
                    x=sub["ANO"],
                    y=sub["VOTOS"],
                    mode="lines+markers",
                    name=cargo,
                    line=dict(width=3, color=_COLORS[i % len(_COLORS)]),
                    marker=dict(size=10),
                    text=[f"{v:,.0f}" for v in sub["VOTOS"]],
                    hovertemplate="%{x}: %{text} votos<extra>%{fullData.name}</extra>",
                )
            )

        fig.update_layout(
            xaxis=dict(
                title="Ano",
                tickmode="array",
                tickvals=sorted(data["ANO"].unique()),
            ),
            yaxis_title="Total de Votos",
            legend_title="Cargo",
            hovermode="x unified",
            margin=dict(l=10, r=10, t=10, b=40),
            plot_bgcolor="white",
            paper_bgcolor="white",
        )
        return fig
