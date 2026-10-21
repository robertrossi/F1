# 🏎️ F1 — volta rápida

### Entre no cockpit e explore as voltas mais rápidas da Fórmula 1.

Um dashboard interativo feito com Streamlit e alimentado pela [API OpenF1](https://openf1.org/). Escolha uma temporada e um circuito para descobrir as cinco voltas válidas mais rápidas em sessões de corrida.

☁️ Quer experimentar sem instalar? ☁️ Abrir o dashboard online [https://ggp6xhn2w4eq8fzruzhdeh.streamlit.app/]

## 🎮 O que você pode explorar

1. Escolha uma temporada a partir de 2023.
2. Selecione um circuito.
3. Compare o top 5, com tempo, piloto, equipe, GP e número da volta.

O app consulta a OpenF1 pela internet. A primeira consulta pode levar alguns segundos; os resultados ficam em cache por seis horas para agilizar visitas seguintes.

## 🚦 Instalação e execução

### Pré-requisitos

- Python 3.11.5 ou superior
- [uv](https://docs.astral.sh/uv/getting-started/installation/), para instalar dependências e executar os comandos
- Conexão com a internet para consultar a API OpenF1

### Baixe o projeto e prepare o ambiente

No PowerShell, clone o repositório e entre na pasta:

```powershell
git clone https://github.com/robertrossi/F1.git
cd F1
```

Instale a versão de Python definida pelo projeto e as dependências travadas no `uv.lock`:

```powershell
uv python install 3.11.5
uv sync --locked
```

### Abra o dashboard

Inicie o Streamlit:

```powershell
uv run streamlit run src/f1/dashboard.py
```

O navegador deve abrir automaticamente. Se não abrir, visite [http://localhost:8501](http://localhost:8501). Para encerrar o servidor, volte ao terminal e pressione `Ctrl+C`.

> **Se `uv` iniciar o pyenv em vez do uv:** no PowerShell, rode `Get-Command uv -All`. Se o primeiro resultado estiver em `pyenv-win\shims\uv.bat`, instale o uv independente do pyenv e ajuste o `PATH` para que o executável dele apareça antes desse shim. Abra um novo terminal e confira com `uv --version`.

## 🧪 Rode os testes

Com o ambiente instalado e o terminal na pasta do projeto:

```powershell
uv run pytest
```

O Pytest executa os testes de `tests/unit/` e mostra a cobertura. A configuração do projeto exige pelo menos 50% de cobertura. Os testes usam respostas simuladas e não consultam a OpenF1.

Outras verificações de qualidade:

```powershell
uv run ruff check .
uv run ruff format --check .
```

## 📚 Abra a documentação

Para visualizar a documentação técnica localmente:

```powershell
uv run mkdocs serve
```

Abra o endereço mostrado no terminal, normalmente [http://127.0.0.1:8000](http://127.0.0.1:8000). Para verificar se a documentação compila sem erros:

```powershell
uv run mkdocs build --strict
```

## 🏁 Regras do ranking

- Inclui somente sessões de corrida (`Race`); treinos, classificação e sprint ficam fora.
- Exclui voltas sem tempo válido e voltas de saída dos boxes.
- Ordena pelo menor tempo e retorna até cinco voltas por circuito e temporada.
- Um piloto pode aparecer mais de uma vez no top 5.

## 🗂️ Estrutura do projeto

```text
F1/
├── docs/                         # Documentação publicada com MkDocs
│   ├── arquitetura.md
│   ├── doc_api.md
│   ├── index.md
│   ├── instalacao.md
│   └── uso.md
├── src/f1/
│   ├── api/client.py             # Cliente HTTP da OpenF1
│   ├── services/fastest_laps.py  # Regras e classificação das voltas
│   ├── config.py                 # Configurações do cliente
│   ├── dashboard.py              # Interface Streamlit
│   └── logging_config.py         # Logs estruturados
├── tests/unit/                   # Testes unitários sem chamadas à rede
├── .python-version               # Versão de Python do projeto
├── doc_api.md                    # Resumo dos endpoints OpenF1
├── mkdocs.yml                    # Configuração do site de documentação
├── plan.md                       # Plano e arquitetura inicial
├── pyproject.toml                # Dependências e ferramentas
└── uv.lock                       # Versões travadas das dependências
```

## 🔎 Mais informações

- [Documentação técnica](docs/index.md)
- [Resumo da API OpenF1](doc_api.md)
- [Plano do projeto](plan.md)
- [Padrões de engenharia](SKILL.md)
