# Instalação

O projeto requer Python 3.11.5 ou superior e [uv](https://docs.astral.sh/uv/).

Sincronize o ambiente reproduzível com:

```bash
uv sync --locked
```

Inicie o dashboard Streamlit:

```bash
uv run streamlit run src/f1/dashboard.py
```

O aplicativo consulta dados históricos da OpenF1 e precisa de acesso à internet. Dados em tempo real não fazem parte do escopo.
