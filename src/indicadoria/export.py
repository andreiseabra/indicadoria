"""Exportacao dos indicadores para um Excel pronto para o Power BI."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .data import Indicadores


def exportar_excel(indicadores: Indicadores, resumo: str, caminho_saida: Path) -> Path:
    """Grava um .xlsx com abas separadas para dados brutos, agregados e resumo.

    A aba "dados" fica no formato longo (uma linha por registro), pronta para
    ser usada como fonte de um dashboard no Power BI (Get Data > Excel).
    """
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    resumo_df = pd.DataFrame({"resumo_executivo": resumo.splitlines()})

    with pd.ExcelWriter(caminho_saida, engine="openpyxl") as writer:
        indicadores.dados.to_excel(writer, sheet_name="dados", index=False)
        indicadores.total_por_categoria.to_excel(
            writer, sheet_name="por_categoria", index=False
        )
        indicadores.total_por_responsavel.to_excel(
            writer, sheet_name="por_responsavel", index=False
        )
        indicadores.evolucao_mensal.to_excel(
            writer, sheet_name="evolucao_mensal", index=False
        )
        resumo_df.to_excel(writer, sheet_name="resumo_ia", index=False)

    return caminho_saida
