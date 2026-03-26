"""
Pré-agrega dados_bairros.json → dados_summary.json

O dashboard carrega dados_summary.json (<<1 MB) em vez do
dados_bairros.json completo (17 MB), tornando a abertura muito mais
rápida.

Uso:
    python gerar_summary.py
    python gerar_summary.py --input outro.json --output saida.json
"""

import argparse
import json
import os
from collections import defaultdict


def aggregate(raw: dict, year_filter=None, cargo_filter=None) -> dict:
    """Agrega todos os registros para uma combinação ano+cargo."""
    by_partido: dict[str, int] = defaultdict(int)
    by_cargo:   dict[str, int] = defaultdict(int)
    by_muni:    dict[str, int] = defaultdict(int)
    by_ano:     dict[int, int] = defaultdict(int)
    cand_votos: dict[str, dict] = {}

    partidos:   set[str] = set()
    municipios: set[str] = set()
    bairros:    set[str] = set()
    cand_set:   set[str] = set()
    total_votos = 0

    for cand, records in raw.items():
        cand_total = 0
        cand_cargo = cand_partido = cand_muni = ""
        cand_ano = 0

        for r in records:
            ano, muni, bairro, votos, cargo, partido = r

            if year_filter  and str(ano) != str(year_filter):  continue
            if cargo_filter and cargo != cargo_filter:          continue

            total_votos += votos
            by_partido[partido] += votos
            by_cargo[cargo]     += votos
            by_muni[muni]       += votos
            by_ano[ano]         += votos
            partidos.add(partido)
            municipios.add(muni)
            bairros.add(bairro)
            cand_set.add(cand)
            cand_total += votos

            if votos > 0:
                cand_cargo   = cargo
                cand_partido = partido
                cand_muni    = muni
                cand_ano     = ano

        if cand_total > 0:
            cand_votos[cand] = {
                "v": cand_total,
                "c": cand_cargo,
                "p": cand_partido,
                "m": cand_muni,
                "a": cand_ano,
            }

    def top(d: dict, n: int) -> list:
        return sorted(d.items(), key=lambda x: -x[1])[:n]

    top_cands_raw = sorted(cand_votos.items(), key=lambda x: -x[1]["v"])[:20]
    top_cands = [[name, info] for name, info in top_cands_raw]

    return {
        "votos":         total_votos,
        "candidatos":    len(cand_set),
        "partidos":      len(partidos),
        "municipios":    len(municipios),
        "bairros":       len(bairros),
        "top_partidos":  top(by_partido, 10),
        "by_cargo":      top(by_cargo, 10),
        "top_municipios":top(by_muni, 10),
        "by_ano":        sorted(by_ano.items()),
        "top_candidatos":top_cands,
    }


def build_summary(raw: dict) -> dict:
    anos   = sorted(set(r[0] for v in raw.values() for r in v))
    cargos = sorted(set(r[4] for v in raw.values() for r in v))

    year_options  = [""] + [str(a) for a in anos]
    cargo_options = [""] + list(cargos)

    summary: dict[str, dict] = {}
    total = len(year_options) * len(cargo_options)
    done  = 0

    for yr in year_options:
        for cg in cargo_options:
            key = f"{yr}|{cg}"
            summary[key] = aggregate(raw, yr or None, cg or None)
            done += 1
            print(f"  [{done}/{total}] {key!r:30s} "
                  f"{summary[key]['votos']:>12,} votos", flush=True)

    return {"filters": summary}


def main():
    parser = argparse.ArgumentParser(description="Gera dados_summary.json a partir de dados_bairros.json")
    parser.add_argument("--input",  default="dados_bairros.json",
                        help="Arquivo JSON de entrada (padrão: dados_bairros.json)")
    parser.add_argument("--output", default="dados_summary.json",
                        help="Arquivo JSON de saída (padrão: dados_summary.json)")
    args = parser.parse_args()

    base = os.path.dirname(os.path.abspath(__file__))
    inp  = os.path.join(base, args.input)
    out  = os.path.join(base, args.output)

    print(f"📂 Lendo {inp} …")
    with open(inp, encoding="utf-8") as f:
        raw = json.load(f)
    print(f"   {len(raw):,} candidatos carregados.")

    print("⚙️  Pré-agregando combinações de filtro…")
    summary = build_summary(raw)

    print(f"\n💾 Gravando {out} …")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, separators=(",", ":"))

    size_kb = os.path.getsize(out) / 1024
    print(f"✅ Concluído! {out}  ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
