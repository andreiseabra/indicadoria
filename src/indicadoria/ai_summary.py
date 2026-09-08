"""Geracao de resumo executivo e alertas com apoio de IA.

Prioriza o Google Gemini (GEMINI_API_KEY), por ter camada gratuita. Se nao
houver chave do Gemini, tenta a OpenAI (OPENAI_API_KEY). Sem nenhuma chave
configurada, cai automaticamente em um modo "fallback" baseado em regras,
para que o projeto rode fim-a-fim sem depender de credenciais externas.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

from .data import Indicadores

load_dotenv()

MODELO_GEMINI_PADRAO = "gemini-flash-lite-latest"
MODELO_OPENAI_PADRAO = "gpt-4o-mini"


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

    linhas = [
        "Resumo executivo (modo offline - IA nao configurada ou indisponivel no momento):"
    ]

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
        "- Configure GEMINI_API_KEY (gratuito) ou OPENAI_API_KEY no arquivo .env "
        "para gerar um resumo mais detalhado com apoio de IA."
    )
    return "\n".join(linhas)


def _resumo_gemini(indicadores: Indicadores, chave: str, modelo: str) -> str | None:
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return None

    try:
        cliente = genai.Client(
            api_key=chave,
            http_options=types.HttpOptions(
                timeout=20_000,  # ms (minimo aceito pela API e 10s; 20s da folga para respostas normais)
                retry_options=types.HttpRetryOptions(
                    attempts=1,  # sem retry: se falhar, cai direto para o modo offline
                    initial_delay=1.0,
                    max_delay=1.0,
                ),
            ),
        )
        resposta = cliente.models.generate_content(
            model=modelo, contents=_prompt(indicadores)
        )
        return resposta.text.strip()
    except Exception:
        # Chave invalida, modelo indisponivel, quota excedida, API fora do ar etc.
        # Nesses casos cai para o proximo provedor (ou modo offline) em vez de quebrar o app.
        return None


def _resumo_openai(indicadores: Indicadores, chave: str, modelo: str) -> str | None:
    try:
        from openai import OpenAI
    except ImportError:
        return None

    try:
        cliente = OpenAI(api_key=chave)
        resposta = cliente.chat.completions.create(
            model=modelo,
            messages=[{"role": "user", "content": _prompt(indicadores)}],
            temperature=0.3,
        )
        return resposta.choices[0].message.content.strip()
    except Exception:
        return None


def gerar_resumo(
    indicadores: Indicadores,
    modelo_gemini: str = MODELO_GEMINI_PADRAO,
    modelo_openai: str = MODELO_OPENAI_PADRAO,
) -> str:
    """Gera o resumo executivo, tentando Gemini, depois OpenAI, depois offline.

    Qualquer falha de rede/API (chave invalida, indisponibilidade, quota) e
    absorvida e o proximo provedor e tentado, terminando sempre no resumo
    offline caso nenhuma IA responda.
    """
    chave_gemini = os.getenv("GEMINI_API_KEY")
    if chave_gemini:
        resumo = _resumo_gemini(indicadores, chave_gemini, modelo_gemini)
        if resumo:
            return resumo

    chave_openai = os.getenv("OPENAI_API_KEY")
    if chave_openai:
        resumo = _resumo_openai(indicadores, chave_openai, modelo_openai)
        if resumo:
            return resumo

    return _resumo_fallback(indicadores)
