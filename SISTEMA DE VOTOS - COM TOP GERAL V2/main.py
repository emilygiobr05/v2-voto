"""
main.py — Script principal do Sistema de Análise Eleitoral de Rondônia.

Uso:
    # Gerar relatório HTML estático (index.html) — todos os anos combinados
    python main.py relatorio

    # Gerar relatório para um ano específico
    python main.py relatorio --year 2024

    # Gerar relatórios separados para cada ano disponível
    python main.py relatorio --todos-anos

    # Iniciar servidor Dash interativo
    python main.py servidor

    # Iniciar servidor Dash em modo debug
    python main.py servidor --debug

    # Pré-agregar dados (gerar dados_summary.json)
    python main.py summary

    # Exibir estatísticas dos dados carregados
    python main.py stats
"""

import argparse
import os
import sys
from pathlib import Path

# Garantir que o diretório do projeto está no path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))


# ── Helpers ────────────────────────────────────────────────────────────────────


def _print_banner() -> None:
    print("=" * 60)
    print("  🗳️  Sistema de Análise Eleitoral — Rondônia")
    print("  📊  Dados: Tribunal Superior Eleitoral (TSE)")
    print("  📅  Eleições: 2016 · 2018 · 2020 · 2022 · 2024")
    print("=" * 60)


def _check_data_file() -> bool:
    """Verifica se dados_bairros.json existe."""
    path = BASE_DIR / "dados_bairros.json"
    if not path.exists():
        print(f"❌ Arquivo de dados não encontrado: {path}")
        print("   Certifique-se de que dados_bairros.json está no mesmo diretório.")
        return False
    size_mb = path.stat().st_size / (1024 * 1024)
    print(f"📂 Dados: {path.name}  ({size_mb:.1f} MB)")
    return True


# ── Comandos ───────────────────────────────────────────────────────────────────


def cmd_relatorio(args) -> None:
    """Gera o relatório HTML estático completo com gráficos Plotly."""
    _print_banner()
    if not _check_data_file():
        sys.exit(1)

    from gerar_relatorio import generate_html_report

    if getattr(args, "todos_anos", False):
        # Gerar um relatório por ano
        from src.data_processor import DataProcessor
        proc = DataProcessor(str(BASE_DIR))
        proc.load_data()
        stats = proc.get_summary_stats()
        anos = stats["anos"]
        print(f"\n📅 Gerando relatórios para {len(anos)} anos: {anos}")
        for ano in anos:
            out = str(BASE_DIR / f"relatorio_{ano}.html")
            print(f"\n{'─' * 40}")
            generate_html_report(data_dir=str(BASE_DIR), output_file=out, ano=ano)
        print(f"\n✅ {len(anos)} relatórios gerados com sucesso!")
    else:
        output = args.output or str(BASE_DIR / "index.html")
        generate_html_report(
            data_dir=str(BASE_DIR),
            output_file=output,
            ano=args.year,
        )


def cmd_servidor(args) -> None:
    """Inicia o servidor Dash para uso local ou deploy."""
    _print_banner()
    if not _check_data_file():
        sys.exit(1)

    from src.dashboard import create_dashboard

    app    = create_dashboard(str(BASE_DIR))
    port   = int(os.environ.get("PORT", args.port))
    debug  = os.environ.get("DEBUG", str(args.debug)).lower() == "true"

    print(f"\n🚀 Servidor iniciando em http://localhost:{port}/")
    if debug:
        print("   Modo DEBUG ativado.")
    print("   Pressione Ctrl+C para parar.\n")
    app.run(debug=debug, host="0.0.0.0", port=port)


def cmd_summary(args) -> None:
    """Pré-agrega dados_bairros.json → dados_summary.json."""
    _print_banner()
    if not _check_data_file():
        sys.exit(1)

    print("\n⚙️  Pré-agregando dados...\n")
    from gerar_summary import main as run_summary
    run_summary()


def cmd_stats(args) -> None:
    """Exibe estatísticas dos dados carregados."""
    _print_banner()
    if not _check_data_file():
        sys.exit(1)

    from src.data_processor import DataProcessor

    print("\n📊 Carregando dados...")
    proc = DataProcessor(str(BASE_DIR))
    proc.load_data()
    df    = proc.get_combined_data()
    stats = proc.get_summary_stats()

    total_votos = int(df["VOTOS"].sum())
    total_cands = int(df["CANDIDATO"].nunique())
    total_part  = int(df["PARTIDO"].nunique())
    total_munis = int(df["MUNICÍPIO"].nunique())
    total_bairr = int(df["BAIRRO"].nunique())
    total_recs  = len(df)

    print(f"\n{'─' * 50}")
    print(f"  📋 Registros no DataFrame : {total_recs:>12,}")
    print(f"  🗳️  Total de Votos         : {total_votos:>12,}")
    print(f"  👤  Candidatos únicos      : {total_cands:>12,}")
    print(f"  🏛️  Partidos únicos        : {total_part:>12,}")
    print(f"  🏙️  Municípios             : {total_munis:>12,}")
    print(f"  📍  Localidades (bairros)  : {total_bairr:>12,}")
    print(f"{'─' * 50}")
    print(f"\n  📅 Anos disponíveis : {stats['anos']}")
    print(f"  📂 Cargos           : {stats['cargos']}")

    print(f"\n{'─' * 50}")
    print("  📈 Votos por ano:")
    by_ano = df.groupby("ANO")["VOTOS"].sum().sort_index()
    for ano, v in by_ano.items():
        bar = "█" * int(v / by_ano.max() * 30)
        print(f"    {ano}  {bar:<30s}  {v:>10,}")

    print(f"\n{'─' * 50}")
    print("  📂 Votos por cargo:")
    by_cargo = df.groupby("CARGO")["VOTOS"].sum().sort_values(ascending=False)
    for cargo, v in by_cargo.items():
        bar = "█" * int(v / by_cargo.max() * 30)
        print(f"    {cargo:<20s}  {bar:<30s}  {v:>10,}")

    print(f"\n{'─' * 50}")
    print("  🏙️  Top 10 municípios:")
    top_munis = df.groupby("MUNICÍPIO")["VOTOS"].sum().nlargest(10)
    for i, (muni, v) in enumerate(top_munis.items(), 1):
        print(f"    {i:>2}. {muni:<30s}  {v:>10,}")
    print()


# ── Ponto de entrada ───────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Sistema de Análise Eleitoral — Rondônia",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="comando", metavar="COMANDO")

    # relatorio
    p_rel = sub.add_parser("relatorio", help="Gerar relatório HTML estático")
    p_rel.add_argument(
        "--year", "-y", type=int, default=None,
        help="Ano de análise (padrão: mais recente)",
    )
    p_rel.add_argument(
        "--output", "-o", type=str, default=None,
        help="Arquivo de saída (padrão: index.html)",
    )
    p_rel.add_argument(
        "--todos-anos", action="store_true",
        help="Gerar um relatório separado para cada ano disponível",
    )
    p_rel.set_defaults(func=cmd_relatorio)

    # servidor
    p_srv = sub.add_parser("servidor", help="Iniciar servidor Dash interativo")
    p_srv.add_argument(
        "--port", type=int, default=8050,
        help="Porta HTTP (padrão: 8050)",
    )
    p_srv.add_argument(
        "--debug", action="store_true",
        help="Ativar modo debug do Dash",
    )
    p_srv.set_defaults(func=cmd_servidor)

    # summary
    p_sum = sub.add_parser("summary", help="Pré-agregar dados para dados_summary.json")
    p_sum.set_defaults(func=cmd_summary)

    # stats
    p_st = sub.add_parser("stats", help="Exibir estatísticas dos dados carregados")
    p_st.set_defaults(func=cmd_stats)

    return parser


def main() -> None:
    parser = build_parser()
    args   = parser.parse_args()

    if not args.comando:
        # Sem subcomando: gera relatório HTML por padrão
        print("Nenhum comando especificado. Gerando relatório HTML...\n")
        args.output     = None
        args.year       = None
        args.todos_anos = False
        cmd_relatorio(args)
        return

    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Interrompido pelo usuário.")
        sys.exit(0)
    except FileNotFoundError as exc:
        print(f"\n❌ Arquivo não encontrado: {exc}")
        sys.exit(1)
    except ImportError as exc:
        print(f"\n❌ Dependência ausente: {exc}")
        print("   Execute: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        print(f"\n❌ Erro: {exc}")
        sys.exit(1)
