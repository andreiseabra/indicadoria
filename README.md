# IndicadorIA

Automação de indicadores e relatórios com apoio de Inteligência Artificial, integrada a Excel e Power BI.

O projeto consolida planilhas Excel (vendas, processos ou indicadores operacionais), calcula agregados (por categoria, por responsável e evolução mensal), gera um **resumo executivo com apoio de IA** e exporta tudo em um único `.xlsx` pronto para ser conectado ao **Power BI**.

## Por que este projeto existe

Ideia pensada para reduzir trabalho manual em rotinas de gestão: em vez de tratar planilhas na mão, o script consolida os dados, aponta tendências/desvios com apoio de IA e entrega um arquivo já estruturado para alimentar um dashboard.

## Como funciona

1. **Consolidação** (`data.py`): lê uma ou mais planilhas `.xlsx` com as colunas `data`, `categoria`, `responsavel`, `valor` e junta tudo em uma base única.
2. **Agregação**: calcula totais por categoria, por responsável e evolução mensal.
3. **Resumo com IA** (`ai_summary.py`): usa a API da OpenAI (se `OPENAI_API_KEY` estiver configurada) para gerar um resumo executivo em português, com tendências e alertas. Sem chave configurada, usa um resumo automático baseado em regras (modo offline), para que o projeto funcione fim-a-fim sem depender de credenciais.
4. **Exportação** (`export.py`): grava um `.xlsx` com abas `dados`, `por_categoria`, `por_responsavel`, `evolucao_mensal` e `resumo_ia` — pronto para `Power BI > Obter Dados > Excel`.

## Instalação

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Uso

Gerar uma planilha de exemplo (opcional, para testar sem dados reais):

```bash
python sample_data/gerar_exemplo.py
```

Rodar a automação:

```bash
python -m indicadoria.cli sample_data/vendas_exemplo.xlsx -o saida/relatorio.xlsx
```

Para usar o resumo gerado por IA em vez do modo offline, defina a variável de ambiente antes de rodar:

```bash
set OPENAI_API_KEY=sua-chave-aqui
```

## Testes

```bash
pip install -e .
pytest
```

## Conectando ao Power BI

No Power BI Desktop: `Obter Dados > Excel` e selecione o arquivo gerado em `saida/`. As abas `por_categoria`, `por_responsavel` e `evolucao_mensal` já vêm prontas para virar cartões, gráficos de barras e linhas do tempo.

## Stack

Python · Pandas · OpenPyXL · API de IA (OpenAI) · Power BI
