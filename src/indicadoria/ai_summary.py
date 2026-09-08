"""Geracao de resumo executivo e alertas com apoio de IA.

Usa a API da OpenAI quando a variavel de ambiente OPENAI_API_KEY esta
configurada. Sem chave configurada, cai automaticamente em um modo
"fallback" baseado em regras, para que o projeto rode fim-a-fim sem
depender de credenciais externas (util para demonstracao e testes).
"""

from __future__ import annotations

import os

from .data import Indicadores

MODELO_PADRAO = "gpt-4o-mini"


def _prompt(indicadores: Indicadores) -> str:
    categorias = indicadores.total_por_categoria.to_string(index=False)
    responsaveis = indicadores.total_por_responsavel.to_string(index=False)
    evolucao = indicadores.evolucao_mensal.to_string(index=False)

    return (
        "Voce e um analista de indicadores. Com base nos dados agregados abaixo, "
        "escreva um resumo executivo curto (ate 6 linhas), em portugues, destacando "
        "tendencias, possiveis desvios/alertas e uma sugestao de melhoria continua.\n\n"
        f"Total por categoria:\n{categorias}\n\n"
        f"Total por responsavel:\n{responsaveis}\n\n"
        f"Evolucao mensal:\n{evolucao}\n"
    )


def _resumo_fallback(indicadores: Indicadores) -> str:
    """Resumo baseado em regras simples, sem chamar nenhuma API externa."""
    cat = indicadores.total_por_categoria
    evolucao = indicadores.evolucao_mensal

    linhas = ["Resumo executivo (modo offline - sem chave de IA configurada):"]

    if not cat.empty:
        top = cat.iloc[0]
        linhas.append(
            f"- Categoria com maior volume: {top['categoria']} "
            f"(R$ {top['valor']:,.2f})."
        )

    if len(evolucao) >= 2:
        atual = evolucao.iloc[-1]["valor"]
        anterior = evolucao.iloc[-2]["valor"]
        if anterior:
            variacao = (atual - anterior) / anterior * 100
            direcao = "alta" if variacao >= 0 else "queda"
            linhas.append(
                f"- Ultimo mes apresentou {direcao} de {abs(variacao):.1f}% "
                "em relacao ao mes anterior."
            )
    linhas.append(
        "- Configure a variavel OPENAI_API_KEY para gerar um resumo mais "
        "detalhado com apoio de IA."
    )
    return "\n".join(linhas)


def gerar_resumo(indicadores: Indicadores, modelo: str = MODELO_PADRAO) -> str:
    """Gera o resumo executivo. Usa IA se houver chave configurada."""
    chave = os.getenv("OPENAI_API_KEY")
    if not chave:
        return _resumo_fallback(indicadores)

    try:
        from openai import OpenAI
    except ImportError:
        return _resumo_fallback(indicadores)

    cliente = OpenAI(api_key=chave)
    resposta = cliente.chat.completions.create(
        model=modelo,
        messages=[{"role": "user", "content": _prompt(indicadores)}],
        temperature=0.3,
    )
    return resposta.choices[0].message.content.strip()
