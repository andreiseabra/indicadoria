"""Leitura e consolidacao de planilhas Excel de entrada."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {"data", "categoria", "responsavel", "valor"}


@dataclass
class Indicadores:
    """Resultado da consolidacao de uma base de indicadores."""

    dados: pd.DataFrame
    total_por_categoria: pd.DataFrame
    total_por_responsavel: pd.DataFrame
    evolucao_mensal: pd.DataFrame


def carregar_planilhas(caminhos: list[Path]) -> pd.DataFrame:
    """Le uma ou mais planilhas Excel e retorna um unico DataFrame consolidado.

    Cada planilha deve conter as colunas: data, categoria, responsavel, valor.
    Planilhas com colunas extras sao aceitas; colunas ausentes geram erro.
    """
    partes = []
    for caminho in caminhos:
        df = pd.read_excel(caminho)
        df.columns = [str(c).strip().lower() for c in df.columns]
        faltando = REQUIRED_COLUMNS - set(df.columns)
        if faltando:
            raise ValueError(
                f"{caminho.name}: colunas obrigatorias ausentes: {sorted(faltando)}"
            )
        df["arquivo_origem"] = caminho.name
        partes.append(df)

    consolidado = pd.concat(partes, ignore_index=True)
    consolidado["data"] = pd.to_datetime(consolidado["data"])
    consolidado["valor"] = pd.to_numeric(consolidado["valor"], errors="coerce").fillna(0)
    return consolidado.sort_values("data").reset_index(drop=True)


def calcular_indicadores(dados: pd.DataFrame) -> Indicadores:
    """Calcula agregados usados no relatorio e no dashboard de Power BI."""
    total_por_categoria = (
        dados.groupby("categoria", as_index=False)["valor"]
        .sum()
        .sort_values("valor", ascending=False)
    )

    total_por_responsavel = (
        dados.groupby("responsavel", as_index=False)["valor"]
        .sum()
        .sort_values("valor", ascending=False)
    )

    mensal = dados.copy()
    mensal["mes"] = mensal["data"].dt.to_period("M").astype(str)
    evolucao_mensal = (
        mensal.groupby("mes", as_index=False)["valor"].sum().sort_values("mes")
    )

    return Indicadores(
        dados=dados,
        total_por_categoria=total_por_categoria,
        total_por_responsavel=total_por_responsavel,
        evolucao_mensal=evolucao_mensal,
    )
