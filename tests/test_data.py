from pathlib import Path

import pandas as pd

from indicadoria.data import calcular_indicadores, carregar_planilhas

DADOS_TESTE = Path(__file__).parent / "dados_teste.xlsx"


def _criar_planilha_teste() -> None:
    df = pd.DataFrame(
        {
            "data": ["2026-01-01", "2026-01-15", "2026-02-01"],
            "categoria": ["Credito Imobiliario", "Consultoria", "Credito Imobiliario"],
            "responsavel": ["Ana", "Bruno", "Ana"],
            "valor": [1000, 500, 2000],
        }
    )
    df.to_excel(DADOS_TESTE, index=False)


def setup_module() -> None:
    _criar_planilha_teste()


def teardown_module() -> None:
    if DADOS_TESTE.exists():
        DADOS_TESTE.unlink()


def test_carregar_planilhas_consolida_colunas():
    dados = carregar_planilhas([DADOS_TESTE])
    assert set(dados.columns) >= {"data", "categoria", "responsavel", "valor"}
    assert len(dados) == 3


def test_calcular_indicadores_agrega_por_categoria():
    dados = carregar_planilhas([DADOS_TESTE])
    indicadores = calcular_indicadores(dados)

    total_credito = indicadores.total_por_categoria.set_index("categoria").loc[
        "Credito Imobiliario", "valor"
    ]
    assert total_credito == 3000

    assert len(indicadores.evolucao_mensal) == 2
