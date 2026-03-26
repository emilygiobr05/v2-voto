"""
ElectoralAnalytics — análises e estatísticas sobre o DataFrame eleitoral.
"""

import pandas as pd
from collections import defaultdict

from .data_processor import DataProcessor, _ELEITOS_POR_CARGO


class ElectoralAnalytics:
    """Calcula indicadores eleitorais a partir do DataFrame principal."""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    # ── Relatório resumo ───────────────────────────────────────────

    def generate_electoral_report(self, ano: int = None) -> dict:
        """
        Gera dicionário com resumo e eleitos por partido.

        Retorna:
            {
                "resumo": { total_votos, total_candidatos,
                            total_partidos, total_municipios },
                "eleitos_por_partido": { partido: n_eleitos, ... }
            }
        """
        df = self.df if ano is None else self.df[self.df["ANO"] == ano]

        resumo = {
            "total_votos":      int(df["VOTOS"].sum()),
            "total_candidatos": int(df["CANDIDATO"].nunique()),
            "total_partidos":   int(df["PARTIDO"].nunique()),
            "total_municipios": int(df["MUNICÍPIO"].nunique()),
        }

        eleitos_por_partido: dict[str, int] = defaultdict(int)

        # Prefeito: 1 por município
        sub = df[df["CARGO"] == "Prefeito"]
        if not sub.empty:
            by_cand = (
                sub.groupby(["CANDIDATO", "PARTIDO", "MUNICÍPIO"])["VOTOS"]
                .sum()
                .reset_index()
            )
            for muni in by_cand["MUNICÍPIO"].unique():
                row = by_cand[by_cand["MUNICÍPIO"] == muni].nlargest(1, "VOTOS").iloc[0]
                eleitos_por_partido[row["PARTIDO"]] += 1

        # Outros cargos estaduais/federais por número fixo de vagas
        for cargo, n_vagas in _ELEITOS_POR_CARGO.items():
            sub = df[df["CARGO"] == cargo]
            if sub.empty:
                continue
            by_cand = (
                sub.groupby(["CANDIDATO", "PARTIDO"])["VOTOS"]
                .sum()
                .reset_index()
                .nlargest(n_vagas, "VOTOS")
            )
            for _, row in by_cand.iterrows():
                eleitos_por_partido[row["PARTIDO"]] += 1

        eleitos_por_partido = dict(
            sorted(eleitos_por_partido.items(), key=lambda x: -x[1])
        )

        return {"resumo": resumo, "eleitos_por_partido": eleitos_por_partido}

    # ── Força partidária ───────────────────────────────────────────

    def analyze_party_strength(self, ano: int = None) -> pd.DataFrame:
        """
        Retorna DataFrame com métricas por partido.

        Colunas: PARTIDO, TOTAL_VOTOS, CANDIDATOS, ELEITOS,
                 PERCENTUAL_VOTOS, TAXA_ELEICAO, CAPILARIDADE
        """
        df = self.df if ano is None else self.df[self.df["ANO"] == ano]

        total_votos_geral = df["VOTOS"].sum() or 1
        total_municipios   = max(df["MUNICÍPIO"].nunique(), 1)

        base = (
            df.groupby("PARTIDO")
            .agg(
                TOTAL_VOTOS=("VOTOS", "sum"),
                CANDIDATOS=("CANDIDATO", "nunique"),
                NUM_MUNICIPIOS=("MUNICÍPIO", "nunique"),
            )
            .reset_index()
            .sort_values("TOTAL_VOTOS", ascending=False)
            .reset_index(drop=True)
        )

        base["PERCENTUAL_VOTOS"] = base["TOTAL_VOTOS"] / total_votos_geral * 100
        base["CAPILARIDADE"]     = base["NUM_MUNICIPIOS"] / total_municipios * 100

        # Eleitos aproximados
        report = self.generate_electoral_report(ano)
        eleitos_map = report["eleitos_por_partido"]
        base["ELEITOS"] = base["PARTIDO"].map(lambda p: eleitos_map.get(p, 0))
        base["TAXA_ELEICAO"] = (
            base["ELEITOS"] / base["CANDIDATOS"].replace(0, 1) * 100
        )

        return base.drop(columns=["NUM_MUNICIPIOS"])
