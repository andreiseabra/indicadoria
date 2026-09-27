# IndicadorIA

Automação de indicadores e relatórios com apoio de Inteligência Artificial, integrada a Excel e Power BI — com **dashboard visual em Streamlit**.

O projeto consolida planilhas Excel (vendas, processos ou indicadores operacionais), calcula agregados (por categoria, por responsável e evolução mensal), gera um **resumo executivo com apoio de IA** e exporta tudo em um único `.xlsx` pronto para ser conectado ao **Power BI**. Tudo isso pode ser feito tanto por linha de comando quanto por um **dashboard web local**, com upload de planilha, gráficos e download do relatório.

## Por que este projeto existe

Ideia pensada para reduzir trabalho manual em rotinas de gestão: em vez de tratar planilhas na mão, o app consolida os dados, aponta tendências/desvios com apoio de IA e entrega um arquivo já estruturado para alimentar um dashboard — sem precisar mexer em código para usar no dia a dia.

## Como funciona

1. **Consolidação** (`data.py`): lê uma ou mais planilhas `.xlsx` com as colunas `data`, `categoria`, `responsavel`, `valor` e junta tudo em uma base única.
2. **Agregação**: calcula totais por categoria, por responsável e evolução mensal.
3. **Resumo com IA** (`ai_summary.py`): usa o **Google Gemini** (se `GEMINI_API_KEY` estiver configurada) para gerar um resumo executivo em português, com tendências e alertas. Sem chave configurada — ou se a API do Gemini estiver instável no momento —, cai automaticamente em um resumo por regras (modo offline), para que o projeto funcione fim-a-fim sem depender de credenciais nem travar por instabilidade externa. A OpenAI é usada como alternativa caso `OPENAI_API_KEY` esteja configurada no lugar do Gemini.
4. **Exportação** (`export.py`): grava um `.xlsx` com abas `dados`, `por_categoria`, `por_responsavel`, `evolucao_mensal` e `resumo_ia` — pronto para `Power BI > Obter Dados > Excel`.
5. **Dashboard** (`app.py`): interface em Streamlit que faz upload da planilha, roda os passos acima e mostra tudo visualmente na tela.

## Instalação

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Como rodar — Dashboard (Streamlit)

Forma recomendada de usar o projeto: interface visual local, sem precisar digitar comandos para cada relatório.

```bash
streamlit run app.py
```

Abre automaticamente em `http://localhost:8501`. Na tela é possível:

- Fazer upload de uma ou mais planilhas `.xlsx`, ou marcar "Usar planilha de exemplo" para testar sem dados reais;
- Ver cartões com valor total, número de categorias e de responsáveis;
- Visualizar gráficos de evolução mensal, total por categoria e total por responsável;
- Ler o resumo executivo gerado (com IA, se o `.env` estiver configurado, ou no modo offline);
- Consultar a tabela de dados consolidados;
- Clicar em **"Gerar Excel para Power BI"** e baixar o arquivo pronto direto pelo navegador.

## Versão web (navegador, sem servidor)

O `index.html` publica o dashboard como site estático: o Streamlit roda direto no navegador do visitante via [stlite](https://github.com/whitphx/stlite) (Python em WebAssembly). É assim que o projeto fica no ar na Netlify, sem servidor Python.

- O `netlify.toml` já configura o deploy (sem build, publicando a raiz do repositório).
- Na primeira visita o navegador baixa o Python, o que leva alguns segundos; depois fica em cache.
- A opção "Usar planilha de exemplo" gera a planilha na hora, sem precisar versionar o `.xlsx`.
- O resumo executivo usa sempre o **modo offline**: uma chave de IA nessa versão ficaria exposta para qualquer visitante. Para o resumo com IA, rode localmente (ou em um servidor) com o `.env` configurado.

Para testar a versão web localmente:

```bash
python -m http.server 8000
```

Depois abra `http://localhost:8000`. Ao criar um módulo novo em `src/indicadoria`, inclua o arquivo na lista `files` do `index.html`.

## Como rodar — Linha de comando (CLI)

Alternativa para uso em scripts, automações agendadas ou pipelines, sem interface gráfica.

Gerar uma planilha de exemplo (opcional, para testar sem dados reais):

```bash
python sample_data/gerar_exemplo.py
```

Rodar a automação:

```bash
python -m indicadoria.cli sample_data/vendas_exemplo.xlsx -o saida/relatorio.xlsx
```

## Usando o resumo com IA (Google Gemini)

Por padrão, sem nenhuma chave configurada, o resumo executivo é gerado em **modo offline** (regras simples sobre os agregados, sem chamar nenhuma API). Para ativar o resumo gerado por IA de verdade, o projeto usa o **Google Gemini**, que tem camada gratuita — não precisa de cartão de crédito para começar.

### 1. Gerar uma chave de API do Gemini (gratuita)

1. Acesse https://aistudio.google.com/apikey (Google AI Studio).
2. Faça login com uma conta Google.
3. Clique em **"Create API key"** (criar chave de API).
4. Escolha ou crie um projeto do Google Cloud quando solicitado (pode usar um projeto novo, é automático).
5. Copie a chave gerada — ela começa com `AIza...`.

A camada gratuita do Gemini tem limite de requisições por minuto/dia, mais que suficiente para rodar este projeto em uso pessoal ou de portfólio.

### 2. Configurar o `.env`

Na raiz do projeto, copie o arquivo de exemplo e edite com a sua chave:

```bash
copy .env.example .env
```

Abra o `.env` gerado e preencha:

```
GEMINI_API_KEY=cole-sua-chave-aqui
OPENAI_API_KEY=
```

- **`GEMINI_API_KEY`**: chave do Google Gemini, usada por padrão sempre que estiver preenchida.
- **`OPENAI_API_KEY`**: opcional, usada apenas como alternativa caso a chave do Gemini não esteja configurada.

O `.env` é lido automaticamente (via `python-dotenv`) tanto pelo dashboard quanto pela CLI, e **nunca é versionado** — já está listado no `.gitignore`, então a chave fica só na sua máquina.

### 3. Rodar com IA ativada

Com o `.env` preenchido, é só rodar normalmente:

```bash
streamlit run app.py
```

ou

```bash
python -m indicadoria.cli sample_data/vendas_exemplo.xlsx -o saida/relatorio.xlsx
```

O projeto usa o modelo `gemini-flash-lite-latest` por padrão (rápido e dentro da camada gratuita). Se a chave for inválida, a quota estourar ou a API do Gemini estiver temporariamente indisponível, o app **não quebra**: registra a falha internamente e devolve o resumo em modo offline automaticamente.

## Testes

```bash
pip install -e .
pytest
```

## Conectando ao Power BI

No Power BI Desktop: `Obter Dados > Excel` e selecione o arquivo gerado (pela CLI em `saida/` ou baixado pelo dashboard). As abas `por_categoria`, `por_responsavel` e `evolucao_mensal` já vêm prontas para virar cartões, gráficos de barras e linhas do tempo.

## Stack

Python · Pandas · OpenPyXL · Streamlit · Google Gemini API (com fallback para OpenAI) · Power BI
