"""Interface de linha de comando do IndicadorIA."""

from __future__ import annotations

import argparse
from pathlib import Path

from .ai_summary import gerar_resumo
from .data import calcular_indicadores, carregar_planilhas
from .export import exportar_excel


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="indicadoria",
        description=(
            "Consolida planilhas Excel, gera um resumo executivo com apoio de IA "
            "e exporta um arquivo pronto para o Power BI."
        ),
    )
    parser.add_argument(
        "entradas",
        nargs="+",
        type=Path,
        help="Uma ou mais planilhas .xlsx de entrada (mesmas colunas).",
    )
    parser.add_argument(
        "-o",
        "--saida",
        type=Path,
        default=Path("saida/indicadores_consolidados.xlsx"),
        help="Caminho do Excel de saida (padrao: saida/indicadores_consolidados.xlsx).",
    )
    parser.add_argument(
        "--modelo",
        default="gpt-4o-mini",
        help="Modelo de IA usado para o resumo executivo, quando OPENAI_API_KEY estiver definido.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = construir_parser()
    args = parser.parse_args(argv)

    dados = carregar_planilhas(args.entradas)
    indicadores = calcular_indicadores(dados)
    resumo = gerar_resumo(indicadores, modelo=args.modelo)
    destino = exportar_excel(indicadores, resumo, args.saida)

    print(f"Relatorio gerado em: {destino}")
    print()
    print(resumo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
