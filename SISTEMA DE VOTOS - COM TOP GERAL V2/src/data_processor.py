"""
DataProcessor — carrega dados_bairros.json e fornece DataFrames para análise.

Estrutura do dados_bairros.json:
    { "NOME DO CANDIDATO": [[ano, municipio, bairro, votos, cargo, partido], ...], ... }
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict


# Número aproximado de eleitos por cargo no estado de Rondônia
_ELEITOS_POR_CARGO = {
    "Governador":       1,
    "Senador":          2,   # 2 senadores por ciclo (1 por eleição)
    "Deputado Federal": 8,
    "Deputado Estadual": 24,
}


class DataProcessor:
    """Carrega e prepara os dados eleitorais."""

    def __init__(self, data_dir: str = "."):
        self.data_dir = Path(data_dir)
        self._raw: dict = {}
        self.df: pd.DataFrame = pd.DataFrame()

    # ── Carregamento ───────────────────────────────────────────────

    def load_data(self) -> None:
        """Lê dados_bairros.json e monta o DataFrame principal."""
        path = self.data_dir / "dados_bairros.json"
        with open(path, encoding="utf-8") as f:
            self._raw = json.load(f)

        records = []
        for candidato, recs in self._raw.items():
            for r in recs:
                ano, muni, bairro, votos, cargo, partido = r
                records.append(
                    {
                        "CANDIDATO": candidato,
                        "ANO":       int(ano),
                        "MUNICÍPIO": muni,
                        "BAIRRO":    bairro,
                        "VOTOS":     int(votos),
                        "CARGO":     cargo,
                        "PARTIDO":   partido,
                    }
                )

        self.df = pd.DataFrame(records)

    # ── Acesso genérico ────────────────────────────────────────────

    def get_combined_data(self) -> pd.DataFrame:
        """Retorna o DataFrame completo."""
        return self.df

    def get_summary_stats(self) -> dict:
        """Resumo rápido: anos, cargos, municípios disponíveis."""
        return {
            "anos":      sorted(self.df["ANO"].unique().tolist()),
            "cargos":    sorted(self.df["CARGO"].unique().tolist()),
            "municipios": sorted(self.df["MUNICÍPIO"].unique().tolist()),
        }

    # ── Candidatos ─────────────────────────────────────────────────

    def get_votes_by_candidate(self, ano: int = None) -> pd.DataFrame:
        """
        Retorna DataFrame com total de votos por candidato.

        Colunas: CANDIDATO, PARTIDO, CARGO, MUNICÍPIO, TOTAL_VOTOS, STATUS
        """
        df = self.df if ano is None else self.df[self.df["ANO"] == ano]

        result = (
            df.groupby(["CANDIDATO", "PARTIDO", "CARGO", "MUNICÍPIO"])
            .agg(TOTAL_VOTOS=("VOTOS", "sum"))
            .reset_index()
            .sort_values("TOTAL_VOTOS", ascending=False)
            .reset_index(drop=True)
        )

        result["STATUS"] = "NÃO ELEITO"
        self._marcar_eleitos(result)
        return result

    def _marcar_eleitos(self, df: pd.DataFrame) -> None:
        """Marca candidatos eleitos com heurística baseada no número de vagas."""
        for cargo in df["CARGO"].unique():
            mask_cargo = df["CARGO"] == cargo

            if cargo == "Prefeito":
                # 1 prefeito por município
                for muni in df.loc[mask_cargo, "MUNICÍPIO"].unique():
                    mask = mask_cargo & (df["MUNICÍPIO"] == muni)
                    idx = df.loc[mask, "TOTAL_VOTOS"].idxmax()
                    df.loc[idx, "STATUS"] = "ELEITO"

            elif cargo == "Vereador":
                # Câmara proporcional — aprox. 9–21 vereadores por porte
                for muni in df.loc[mask_cargo, "MUNICÍPIO"].unique():
                    mask = mask_cargo & (df["MUNICÍPIO"] == muni)
                    total_cands = mask.sum()
                    n_vagas = max(9, min(21, int(total_cands * 0.12)))
                    idxs = df.loc[mask].nlargest(n_vagas, "TOTAL_VOTOS").index
                    df.loc[idxs, "STATUS"] = "ELEITO"

            else:
                n_vagas = _ELEITOS_POR_CARGO.get(cargo, 1)
                idxs = df.loc[mask_cargo].nlargest(n_vagas, "TOTAL_VOTOS").index
                df.loc[idxs, "STATUS"] = "ELEITO"

    # ── Municípios ─────────────────────────────────────────────────

    def get_votes_by_municipality(self, ano: int = None) -> pd.DataFrame:
        """
        Retorna DataFrame com totais por município.

        Colunas: MUNICÍPIO, TOTAL_VOTOS, ELEITORADO, NUM_CANDIDATOS,
                 NUM_PARTIDOS, PARTICIPACAO
        """
        df = self.df if ano is None else self.df[self.df["ANO"] == ano]

        result = (
            df.groupby("MUNICÍPIO")
            .agg(
                TOTAL_VOTOS=("VOTOS", "sum"),
                NUM_CANDIDATOS=("CANDIDATO", "nunique"),
                NUM_PARTIDOS=("PARTIDO", "nunique"),
            )
            .reset_index()
            .sort_values("TOTAL_VOTOS", ascending=False)
            .reset_index(drop=True)
        )

        # Estimativa de eleitorado: votos totais / taxa média de comparecimento
        result["ELEITORADO"] = (result["TOTAL_VOTOS"] / 0.82).astype(int)
        result["PARTICIPACAO"] = 82.0
        return result
