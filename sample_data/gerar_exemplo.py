"""Gera uma planilha de exemplo para testar o IndicadorIA sem dados reais."""

from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

CATEGORIAS = ["Credito Imobiliario", "Renegociacao", "Consultoria", "Documentacao"]
RESPONSAVEIS = ["Ana", "Bruno", "Carla", "Diego"]


def gerar(n: int = 120, seed: int = 42) -> pd.DataFrame:
    random.seed(seed)
    inicio = date(2026, 1, 1)
    linhas = []
    for i in range(n):
        linhas.append(
            {
                "data": inicio + timedelta(days=random.randint(0, 240)),
                "categoria": random.choice(CATEGORIAS),
                "responsavel": random.choice(RESPONSAVEIS),
                "valor": round(random.uniform(500, 15000), 2),
            }
        )
    return pd.DataFrame(linhas)


if __name__ == "__main__":
    destino = Path(__file__).parent / "vendas_exemplo.xlsx"
    gerar().to_excel(destino, index=False)
    print(f"Arquivo de exemplo gerado em: {destino}")
