"""
main.py — Script principal do Sistema de Análise Eleitoral de Rondônia.

Uso:
    # Gerar relatório HTML estático (index.html)
    python main.py relatorio

    # Gerar relatório para um ano específico
    python main.py relatorio --year 2024

    # Iniciar servidor Dash interativo
    python main.py servidor

    # Pré-agregar dados (gerar dados_summary.json)
    python main.py summary
"""

import argparse
import os
import sys
from pathlib import Path

# Garantir que o diretório do projeto está no path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))


# ── Comandos ───────────────────────────────────────────────────────────────────


def cmd_relatorio(args) -> None:
    """Gera o relatório HTML estático completo com gráficos Plotly."""
    from gerar_relatorio import generate_html_report

    output = args.output or str(BASE_DIR / "index.html")
    generate_html_report(
        data_dir=str(BASE_DIR),
        output_file=output,
        ano=args.year,
    )


def cmd_servidor(args) -> None:
    """Inicia o servidor Dash para uso local ou deploy."""
    from src.dashboard import create_dashboard

    app    = create_dashboard(str(BASE_DIR))
    port   = int(os.environ.get("PORT", args.port))
    debug  = os.environ.get("DEBUG", str(args.debug)).lower() == "true"

    print(f"🚀 Servidor iniciando em http://localhost:{port}/")
    print("   Pressione Ctrl+C para parar.\n")
    app.run(debug=debug, host="0.0.0.0", port=port)


def cmd_summary(args) -> None:
    """Pré-agrega dados_bairros.json → dados_summary.json."""
    from gerar_summary import main as run_summary

    run_summary()


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

    return parser


def main() -> None:
    parser = build_parser()
    args   = parser.parse_args()

    if not args.comando:
        # Sem subcomando: gera relatório HTML por padrão
        print("Nenhum comando especificado. Gerando relatório HTML...\n")
        args.output = None
        args.year   = None
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
