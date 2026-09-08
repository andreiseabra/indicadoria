"""Dashboard Streamlit do IndicadorIA.

Roda localmente com: streamlit run app.py
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from indicadoria.ai_summary import gerar_resumo
from indicadoria.data import calcular_indicadores, carregar_planilhas
from indicadoria.export import exportar_excel

st.set_page_config(page_title="IndicadorIA", layout="wide")

st.markdown(
    """
    <style>
    #MainMenu, header [data-testid="stToolbar"], [data-testid="stStatusWidget"] {
        visibility: hidden;
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("IndicadorIA")
st.caption("Automação de indicadores e relatórios com apoio de IA, Excel e Power BI.")

arquivos = st.file_uploader(
    "Envie uma ou mais planilhas Excel (colunas: data, categoria, responsavel, valor)",
    type=["xlsx"],
    accept_multiple_files=True,
)

usar_exemplo = st.checkbox("Usar planilha de exemplo (sample_data/vendas_exemplo.xlsx)")

caminhos: list[Path] = []
tmpdir = None

if usar_exemplo:
    exemplo = Path(__file__).parent / "sample_data" / "vendas_exemplo.xlsx"
    if exemplo.exists():
        caminhos = [exemplo]
    else:
        st.warning(
            "Exemplo não encontrado. Rode `python sample_data/gerar_exemplo.py` primeiro."
        )
elif arquivos:
    tmpdir = tempfile.TemporaryDirectory()
    for arquivo in arquivos:
        destino = Path(tmpdir.name) / arquivo.name
        destino.write_bytes(arquivo.getvalue())
        caminhos.append(destino)

if caminhos:
    try:
        dados = carregar_planilhas(caminhos)
        indicadores = calcular_indicadores(dados)
    except ValueError as erro:
        st.error(str(erro))
        st.stop()

    total = indicadores.dados["valor"].sum()
    categorias = indicadores.dados["categoria"].nunique()
    responsaveis = indicadores.dados["responsavel"].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Valor total", f"R$ {total:,.2f}")
    col2.metric("Categorias", categorias)
    col3.metric("Responsáveis", responsaveis)

    st.subheader("Evolução mensal")
    st.line_chart(indicadores.evolucao_mensal.set_index("mes"))

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Total por categoria")
        st.bar_chart(indicadores.total_por_categoria.set_index("categoria"))
    with col_b:
        st.subheader("Total por responsável")
        st.bar_chart(indicadores.total_por_responsavel.set_index("responsavel"))

    st.subheader("Resumo executivo")
    with st.spinner("Gerando resumo..."):
        resumo = gerar_resumo(indicadores)
    st.info(resumo)

    st.subheader("Dados consolidados")
    st.dataframe(indicadores.dados, use_container_width=True)

    if st.button("Gerar Excel para Power BI"):
        destino = Path("saida/indicadores_consolidados.xlsx")
        exportar_excel(indicadores, resumo, destino)
        with open(destino, "rb") as f:
            st.download_button(
                "Baixar Excel gerado",
                data=f,
                file_name=destino.name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
else:
    st.info("Envie uma planilha ou marque a opção de usar o exemplo para começar.")
